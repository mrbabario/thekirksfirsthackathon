from __future__ import annotations

from typing import cast

from algo.cache import Cache, article_hash
from algo.config import Settings
from algo.llm.gemma import GemmaClient
from algo.models import *
from algo.retrieval.pubmed import PubMedClient
from algo.retrieval.ranking import Ranker


class FactChecker:

    def __init__(
        self,
        settings: Settings,
    ):

        self.settings = settings

        # ----------------------------------------------------
        # Cache
        # ----------------------------------------------------

        self.cache = Cache(settings.CACHE_DB)

        # ----------------------------------------------------
        # Gemma
        # ----------------------------------------------------

        self.gemma = GemmaClient(settings.GEMMA_MODEL)

        # ----------------------------------------------------
        # PubMed
        # ----------------------------------------------------

        self.pubmed = PubMedClient(
            base_url=settings.PUBMED_BASE_URL,
            cache=self.cache,
            email=settings.PUBMED_EMAIL,
            api_key=settings.PUBMED_API_KEY,
        )

        # ----------------------------------------------------
        # Ranking
        # ----------------------------------------------------

        self.ranker = Ranker(
            embedding_model_name=(settings.EMBEDDING_MODEL),
            cross_encoder_model_name=(settings.CROSS_ENCODER_MODEL),
        )

    # ========================================================
    # MAIN ALGORITHM
    # ========================================================

    def check_article(self, article: str) -> ArticleResult:
      print("[START] check_article()", flush=True)

      article = self._normalize_article(article)
      print(f"[INFO] Article length: {len(article)} characters", flush=True)

      article_hash_value = article_hash(article)
      print(f"[INFO] Hash: {article_hash_value}", flush=True)

      cached = self.cache.get_article(
          article_hash_value,
          self.settings.PIPELINE_VERSION,
      )

      if cached is not None:
          print(
              f"[CACHE] Article hit: {article_hash_value}",
              flush=True,
          )
          return cached

      print(
          f"[CACHE] Article miss: {article_hash_value}",
          flush=True,
      )

      # --------------------------------------------------
      # GEMMA CLAIM EXTRACTION
      # --------------------------------------------------

      print("[GEMMA] Starting claim extraction...", flush=True)

      language, claims = self.gemma.extract_claims(article)

      print(
          f"[GEMMA] Claim extraction finished. "
          f"Language={language}, Claims={len(claims)}",
          flush=True,
      )

      # --------------------------------------------------
      # CLAIMS
      # --------------------------------------------------

      results = []

      for i, claim in enumerate(claims, start=1):

          print(
              f"\n[CLAIM {i}/{len(claims)}] {claim.text}",
              flush=True,
          )

          result = self._check_claim(claim)

          results.append(result)

          print(
              f"[CLAIM {i}] Finished: {result.verdict}",
              flush=True,
          )

      # --------------------------------------------------
      # SAVE
      # --------------------------------------------------

      result = ArticleResult(
          article_hash=article_hash_value,
          language=language,
          claims=results,
      )

      print("[CACHE] Saving article result...", flush=True)

      self.cache.save_article(
          result,
          self.settings.PIPELINE_VERSION,
      )

      print("[DONE] Article saved to cache.", flush=True)

      return result

    # ========================================================
    # CLAIM PIPELINE
    # ========================================================

    def _check_claim(self, claim: Claim) -> ClaimResult:
      print("[GEMMA] Generating PubMed queries...", flush=True)

      queries = self.gemma.generate_queries(claim)

      print(
          f"[GEMMA] Generated queries: {queries}",
          flush=True,
      )

      pmids = []

      print("[PUBMED] Searching...", flush=True)

      for query in queries:

          print(
              f"[PUBMED] Query: {query}",
              flush=True,
          )

          ids = self.pubmed.search_with_fallback(
              query,
              claim.language,
              self.settings.PUBMED_RESULTS_PER_QUERY,
          )

          print(
              f"[PUBMED] Returned {len(ids)} PMIDs",
              flush=True,
          )

          for pmid in ids:

              if pmid not in pmids:
                  pmids.append(pmid)

              if len(pmids) >= self.settings.MAX_CANDIDATES:
                  break

          if len(pmids) >= self.settings.MAX_CANDIDATES:
              break

      print(
          f"[PUBMED] Total candidates: {len(pmids)}",
          flush=True,
      )

      papers = self.pubmed.fetch(pmids)

      print(
          f"[PUBMED] Fetched {len(papers)} papers",
          flush=True,
      )

      print("[RANKING] Semantic retrieval...", flush=True)

      papers = self.ranker.semantic_retrieve(
          claim,
          papers,
          self.settings.SEMANTIC_TOP_K,
      )

      print(
          f"[RANKING] Semantic top: {len(papers)}",
          flush=True,
      )

      print("[RANKING] Cross-encoder...", flush=True)

      papers = self.ranker.rerank(
          claim,
          papers,
          self.settings.RERANK_TOP_K,
      )

      print(
          f"[RANKING] Final references: {len(papers)}",
          flush=True,
      )

      references = [
          Reference(
              number=i + 1,
              pmid=paper.pmid,
              title=paper.title,
              abstract=paper.abstract,
              journal=paper.journal,
              year=paper.year,
          )
          for i, paper in enumerate(papers)
      ]

      print("[GEMMA] Evaluating claim...", flush=True)

      verdict, explanation = self._get_validated_verdict(
          claim,
          references,
      )

      print(
          f"[GEMMA] Verdict: {verdict}",
          flush=True,
      )

      return ClaimResult(
          claim=claim,
          verdict=verdict,
          explanation=explanation,
          references=references,
      )

    # ========================================================
    # VERDICT + CITATION VALIDATION
    # ========================================================

    def _get_validated_verdict(
        self,
        claim: Claim,
        references: list[Reference],
    ) -> tuple[Verdict, list[ExplanationPart]]:

        if not references:
            return (
                "INSUFFICIENT",
                [
                    ExplanationPart(
                        text="No relevant biomedical references were found.",
                        references=[],
                    )
                ],
            )

        valid_reference_ids = {ref.number for ref in references}

        for attempt in range(2):
            data = self.gemma.compare_claim(
                claim,
                references,
            )

            verdict_raw = data.get("verdict")
            explanation_raw = data.get("explanation")

            # --------------------------------------------------
            # Validate verdict
            # --------------------------------------------------

            valid_verdicts = {
                "SUPPORTED",
                "CONTRADICTED",
                "MIXED",
                "INSUFFICIENT",
            }

            if verdict_raw not in valid_verdicts:
                continue

            verdict = cast(Verdict, verdict_raw)

            # --------------------------------------------------
            # Validate explanation
            # --------------------------------------------------

            explanation: list[ExplanationPart] = []

            if not isinstance(explanation_raw, list):
                continue

            valid = True

            for part in explanation_raw:
              if not isinstance(part, dict):
                  valid = False
                  break

              text = part.get("text")
              citation_ids = part.get("references", [])

              if not isinstance(text, str):
                  valid = False
                  break

              if not isinstance(citation_ids, list):
                  valid = False
                  break

              if not all(
                  isinstance(x, int)
                  for x in citation_ids
              ):
                  valid = False
                  break

              if not self._valid_citations(
                  citation_ids,
                  valid_reference_ids,
              ):
                  valid = False
                  break

              explanation.append(
                  ExplanationPart(
                      text=text,
                      references=citation_ids,
                  )
              )

            if not valid:
                continue

            return verdict, explanation

        # Gemma failed validation twice
        return (
            "INSUFFICIENT",
            [
                ExplanationPart(
                    text="The available evidence could not be reliably evaluated.",
                    references=[],
                )
            ],
        )

    # ========================================================
    # CITATION VALIDATION
    # ========================================================

    def _valid_citations(
        self,
        citations: list[int],
        valid_reference_ids: set[int],
    ) -> bool:

        return all(
            reference_id in valid_reference_ids
            for reference_id in citations
        )

    # ========================================================
    # ARTICLE NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize_article(
        article: str,
    ) -> str:

        lines = [line.strip() for line in article.splitlines()]

        lines = [line for line in lines if line]

        return "\n".join(lines)
