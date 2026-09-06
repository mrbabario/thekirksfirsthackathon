from __future__ import annotations

from dataclasses import asdict

from algo.cache import Cache, article_hash
from algo.config import Settings
from algo.llm.gemma import GemmaClient
from algo.models import (
    ArticleResult,
    Claim,
    ClaimResult,
    ExplanationPart,
    Reference,
    Verdict,
)
from algo.retrieval.pubmed import PubMedClient
from algo.retrieval.ranking import Ranker


class FactChecker:

    def __init__(
        self,
        settings: Settings,
    ):
        self.settings = settings

        self.cache = Cache(
            settings.CACHE_DB
        )

        self.gemma = GemmaClient(
            settings.GEMMA_MODEL
        )

        self.pubmed = PubMedClient(
            settings.PUBMED_BASE_URL,
            self.cache,
            settings.PUBMED_EMAIL,
            settings.PUBMED_API_KEY,
        )

        self.ranker = None

    def _get_ranker(self) -> Ranker:
      if self.ranker is None:
          print(
              "[RANKING] Loading embedding and cross-encoder models...",
              flush=True,
          )

          self.ranker = Ranker(
              self.settings.EMBEDDING_MODEL,
              self.settings.CROSS_ENCODER_MODEL,
          )

          print(
              "[RANKING] Models loaded.",
              flush=True,
          )

      return self.ranker

    # =========================================================
    # ARTICLE
    # =========================================================

    def check_article(
        self,
        article: str,
    ) -> ArticleResult:

        import time
        import traceback

        started = time.perf_counter()

        print("\n" + "=" * 70, flush=True)
        print("DR.KIRK FACT CHECK REQUEST RECEIVED", flush=True)
        print("=" * 70, flush=True)

        try:
            print("[START] check_article()", flush=True)

            article = self._normalize_article(article)

            print(
                f"[INFO] Article length: {len(article)} characters",
                flush=True,
            )

            if not article:
                raise ValueError("Article is empty after normalization.")

            article_hash_value = article_hash(article)

            print(
                f"[INFO] Hash: {article_hash_value}",
                flush=True,
            )

            # ---------------------------------------------------------
            # CACHE
            # ---------------------------------------------------------

            print("[CACHE] Checking article cache...", flush=True)

            cached = self.cache.get_article(
                article_hash_value,
                self.settings.PIPELINE_VERSION,
            )

            if cached is not None:
                print(
                    f"[CACHE] HIT: {article_hash_value}",
                    flush=True,
                )
                print(
                    "[DONE] Returning cached result.",
                    flush=True,
                )
                return cached

            print(
                f"[CACHE] MISS: {article_hash_value}",
                flush=True,
            )

            # ---------------------------------------------------------
            # LANGUAGE + CLAIM EXTRACTION
            # ---------------------------------------------------------

            print(
                "\n[STAGE 1/7] GEMMA CLAIM EXTRACTION",
                flush=True,
            )

            print(
                f"[GEMMA] Model: {self.settings.GEMMA_MODEL}",
                flush=True,
            )

            language, claims = self.gemma.extract_claims(article)

            print(
                f"[GEMMA] Language: {language}",
                flush=True,
            )

            print(
                f"[GEMMA] Claims found: {len(claims)}",
                flush=True,
            )

            for i, claim in enumerate(claims, start=1):
                print(
                    f"[CLAIM {i}] {claim.text}",
                    flush=True,
                )

            # ---------------------------------------------------------
            # CHECK EACH CLAIM
            # ---------------------------------------------------------

            results = []

            for i, claim in enumerate(claims, start=1):

                print("\n" + "-" * 70, flush=True)
                print(
                    f"[CLAIM {i}/{len(claims)}] {claim.text}",
                    flush=True,
                )
                print("-" * 70, flush=True)

                result = self._check_claim(claim)

                results.append(result)

                print(
                    f"[CLAIM {i}] FINISHED → {result.verdict}",
                    flush=True,
                )

            # ---------------------------------------------------------
            # SAVE
            # ---------------------------------------------------------

            print(
                "\n[STAGE 7/7] SAVING RESULT",
                flush=True,
            )

            result = ArticleResult(
                article_hash=article_hash_value,
                language=language,
                claims=results,
            )

            self.cache.save_article(
                result,
                self.settings.PIPELINE_VERSION,
            )

            elapsed = time.perf_counter() - started

            print(
                f"[DONE] Article saved to cache.",
                flush=True,
            )

            print(
                f"[DONE] Total pipeline time: {elapsed:.2f}s",
                flush=True,
            )

            print("=" * 70, flush=True)
            print("DR.KIRK FACT CHECK COMPLETE", flush=True)
            print("=" * 70 + "\n", flush=True)

            return result

        except Exception as e:
            elapsed = time.perf_counter() - started

            print("\n" + "!" * 70, flush=True)
            print("DR.KIRK FACT CHECK FAILED", flush=True)
            print("!" * 70, flush=True)

            print(
                f"[ERROR] Type: {type(e).__name__}",
                flush=True,
            )

            print(
                f"[ERROR] Message: {e}",
                flush=True,
            )

            print(
                f"[ERROR] Runtime: {elapsed:.2f}s",
                flush=True,
            )

            print(
                "\n[ERROR] Full traceback:",
                flush=True,
            )

            traceback.print_exc()

            print("!" * 70 + "\n", flush=True)

            raise

    # =========================================================
    # CLAIM
    # =========================================================

    def _check_claim(
        self,
        claim: Claim,
    ) -> ClaimResult:

        # -----------------------------------------------------
        # QUERY GENERATION
        # -----------------------------------------------------

        print(
            "[GEMMA] Generating PubMed queries...",
            flush=True,
        )

        queries = (
            self.gemma.generate_queries(
                claim
            )
        )

        print(
            f"[GEMMA] Queries: {queries}",
            flush=True,
        )

        # -----------------------------------------------------
        # LANGUAGE-SPECIFIC SEARCH
        # -----------------------------------------------------

        language_pmids: list[str] = []

        for query in queries:

            print(
                f"[PUBMED] Language-specific query: "
                f"{query}",
                flush=True,
            )

            ids = self.pubmed.search(
                query,
                language=claim.language,
                retmax=(
                    self.settings
                    .PUBMED_RESULTS_PER_QUERY
                ),
            )

            for pmid in ids:

                if pmid not in language_pmids:
                    language_pmids.append(
                        pmid
                    )

        print(
            f"[PUBMED] "
            f"{len(language_pmids)} "
            f"{claim.language} candidates",
            flush=True,
        )

        # -----------------------------------------------------
        # FETCH LANGUAGE PAPERS
        # -----------------------------------------------------

        language_papers = (
            self.pubmed.fetch(
                language_pmids
            )
        )

        print(
            f"[PUBMED] Fetched "
            f"{len(language_papers)} "
            f"language-specific papers",
            flush=True,
        )

        # -----------------------------------------------------
        # RANK LANGUAGE PAPERS
        # -----------------------------------------------------

        ranker = self._get_ranker()

        language_papers = (
            ranker.semantic_retrieve(
                claim,
                language_papers,
                self.settings.SEMANTIC_TOP_K,
            )
        )

        language_papers = (
            ranker.rerank(
                claim,
                language_papers,
                self.settings.RERANK_TOP_K,
            )
        )

        print(
            f"[RANKING] "
            f"{len(language_papers)} "
            f"language-specific papers after ranking",
            flush=True,
        )

        # -----------------------------------------------------
        # INTERNATIONAL FALLBACK
        # -----------------------------------------------------

        final_papers = language_papers

        if len(final_papers) < self.settings.RERANK_TOP_K:

            print(
                "[PUBMED] Not enough "
                f"{claim.language} evidence.",
                flush=True,
            )

            print(
                "[PUBMED] Using international fallback.",
                flush=True,
            )

            fallback_pmids: list[str] = []

            for query in queries:

                ids = self.pubmed.search(
                    query,
                    language=None,
                    retmax=(
                        self.settings
                        .PUBMED_RESULTS_PER_QUERY
                    ),
                )

                for pmid in ids:

                    if pmid in language_pmids:
                        continue

                    if pmid not in fallback_pmids:
                        fallback_pmids.append(
                            pmid
                        )

            print(
                f"[PUBMED] "
                f"{len(fallback_pmids)} "
                f"international candidates",
                flush=True,
            )

            fallback_papers = (
                self.pubmed.fetch(
                    fallback_pmids
                )
            )

            needed = (
                self.settings.RERANK_TOP_K
                - len(final_papers)
            )

            fallback_papers = (
                ranker.semantic_retrieve(
                    claim,
                    fallback_papers,
                    self.settings.SEMANTIC_TOP_K,
                )
            )

            fallback_papers = (
                ranker.rerank(
                    claim,
                    fallback_papers,
                    needed,
                )
            )

            final_papers = (
                final_papers
                + fallback_papers
            )

        # -----------------------------------------------------
        # NUMBER REFERENCES
        # -----------------------------------------------------

        references = []

        for i, paper in enumerate(
            final_papers,
            start=1,
        ):

            references.append(
                Reference(
                    number=i,
                    pmid=paper.pmid,
                    title=paper.title,
                    abstract=paper.abstract,
                    journal=paper.journal,
                    year=paper.year,
                )
            )

        print(
            f"[RANKING] Final references: "
            f"{len(references)}",
            flush=True,
        )

        # -----------------------------------------------------
        # CLAIM EVALUATION
        # -----------------------------------------------------

        print(
            "[GEMMA] Evaluating claim...",
            flush=True,
        )

        verdict, explanation = (
            self._get_validated_verdict(
                claim,
                references,
            )
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

    # =========================================================
    # VERDICT + CITATION VALIDATION
    # =========================================================

    def _get_validated_verdict(
        self,
        claim: Claim,
        references: list[Reference],
    ) -> tuple[
        Verdict,
        list[ExplanationPart],
    ]:

        if not references:

            return (
                "INSUFFICIENT",
                [
                    ExplanationPart(
                        text=(
                            "No relevant biomedical "
                            "references were found."
                        ),
                        references=[],
                    )
                ],
            )

        valid_reference_ids = {
            ref.number
            for ref in references
        }

        for attempt in range(2):

            data = (
                self.gemma.compare_claim(
                    claim,
                    references,
                )
            )

            verdict_raw = data.get(
                "verdict"
            )

            # -------------------------------------------------
            # VERDICT VALIDATION
            # -------------------------------------------------

            if verdict_raw == "SUPPORTED":
                verdict: Verdict = "SUPPORTED"

            elif verdict_raw == "CONTRADICTED":
                verdict = "CONTRADICTED"

            elif verdict_raw == "MIXED":
                verdict = "MIXED"

            elif verdict_raw == "INSUFFICIENT":
                verdict = "INSUFFICIENT"

            else:
                print(
                    "[VALIDATION] Invalid verdict.",
                    flush=True,
                )
                continue

            # -------------------------------------------------
            # EXPLANATION VALIDATION
            # -------------------------------------------------

            explanation_raw = data.get(
                "explanation"
            )

            if not isinstance(
                explanation_raw,
                list,
            ):
                continue

            explanation: list[
                ExplanationPart
            ] = []

            valid = True

            for part in explanation_raw:

                if not isinstance(
                    part,
                    dict,
                ):
                    valid = False
                    break

                text = part.get("text")

                citation_ids = part.get(
                    "references",
                    [],
                )

                if not isinstance(
                    text,
                    str,
                ):
                    valid = False
                    break

                if not isinstance(
                    citation_ids,
                    list,
                ):
                    valid = False
                    break

                if not all(
                    isinstance(
                        x,
                        int,
                    )
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
                print(
                    "[VALIDATION] Invalid "
                    "citation structure.",
                    flush=True,
                )
                continue

            return (
                verdict,
                explanation,
            )

        # -----------------------------------------------------
        # FAILED VALIDATION
        # -----------------------------------------------------

        print(
            "[VALIDATION] Gemma failed "
            "validation twice.",
            flush=True,
        )

        return (
            "INSUFFICIENT",
            [
                ExplanationPart(
                    text=(
                        "The available evidence "
                        "could not be reliably evaluated."
                    ),
                    references=[],
                )
            ],
        )

    # =========================================================
    # CITATION VALIDATION
    # =========================================================

    def _valid_citations(
        self,
        citations: list[int],
        valid_reference_ids: set[int],
    ) -> bool:

        return all(
            reference_id
            in valid_reference_ids
            for reference_id in citations
        )

    # =========================================================
    # ARTICLE NORMALIZATION
    # =========================================================

    def _normalize_article(
        self,
        article: str,
    ) -> str:

        return " ".join(
            article.split()
        )
