from typing import Any
import re
import requests
import xml.etree.ElementTree as ET

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search

from ai.models import Claim, Reference
from ai.query_generator import generate_queries


class ReferencesRetriever:

    PUBMED_URL = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    )

    LANGUAGE_CODES = {
        "English": "eng",
        "French": "fre",
        "Malay": "may",
        "Chinese": "chi",
        "Japanese": "jpn",
        "Korean": "kor",
        "German": "ger",
        "Spanish": "spa",
        "Portuguese": "por",
        "Italian": "ita",
        "Russian": "rus",
    }

    STOPWORDS = {
        "the",
        "and",
        "or",
        "of",
        "to",
        "in",
        "a",
        "an",
        "for",
        "on",
        "with",
        "de",
        "des",
        "du",
        "la",
        "le",
        "les",
        "un",
        "une",
        "et",
        "ou",
        "en",
        "dans",
        "pour",
        "avec",
        "sur",
        "à",
        "au",
        "aux",
    }

    def __init__(self):

        self.embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )

    # ---------------------------------------------------------
    # PUBMED SEARCH
    # ---------------------------------------------------------

    def search_pubmed(
        self,
        query: str,
        language: str | None = None,
        max_results: int = 30,
    ) -> list[str]:

        search_query = query

        language_code = (
            self.LANGUAGE_CODES.get(language)
            if language is not None
            else None
        )

        if language_code:
            search_query = (
                f"({query}) AND "
                f"{language_code}[la]"
            )

        params = {
            "db": "pubmed",
            "term": search_query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
        }

        response = requests.get(
            self.PUBMED_URL + "esearch.fcgi",
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()[
            "esearchresult"
        ]["idlist"]

    def search_multiple_queries(
        self,
        queries: list[str],
        language: str | None = None,
        max_results_per_query: int = 30,
    ) -> list[str]:

        pmids = []

        for query in queries:

            try:

                results = self.search_pubmed(
                    query=query,
                    language=language,
                    max_results=max_results_per_query,
                )

                pmids.extend(results)

            except requests.RequestException as e:

                print(
                    f"PubMed search failed for "
                    f"'{query}': {e}"
                )

        return list(
            dict.fromkeys(pmids)
        )

    # ---------------------------------------------------------
    # FETCH
    # ---------------------------------------------------------

    def fetch_pubmed(
        self,
        pmids: list[str],
    ) -> list[dict]:

        if not pmids:
            return []

        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }

        response = requests.get(
            self.PUBMED_URL + "efetch.fcgi",
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.text
        )

        papers = []

        for article in root.findall(
            ".//PubmedArticle"
        ):

            pmid = article.findtext(
                ".//PMID",
                default="",
            )

            title_node = article.find(
                ".//ArticleTitle"
            )

            title = (
                "".join(
                    title_node.itertext()
                ).strip()
                if title_node is not None
                else ""
            )

            abstract_parts = []

            for part in article.findall(
                ".//Abstract/AbstractText"
            ):

                text = "".join(
                    part.itertext()
                ).strip()

                if text:
                    abstract_parts.append(
                        text
                    )

            abstract = " ".join(
                abstract_parts
            )

            journal = article.findtext(
                ".//Journal/Title",
                default="",
            )

            year = ""

            year_node = article.find(
                ".//PubDate/Year"
            )

            if year_node is not None:
                year = (
                    year_node.text
                    or ""
                )

            if not year:

                medline_date = article.findtext(
                    ".//PubDate/MedlineDate",
                    default="",
                )

                if medline_date:
                    year = medline_date[:4]

            languages = [
                node.text.strip()
                for node in article.findall(
                    ".//Language"
                )
                if node.text
            ]

            language = (
                languages[0]
                if languages
                else "unknown"
            )

            papers.append(
                {
                    "pmid": pmid,
                    "title": title,
                    "abstract": abstract,
                    "journal": journal,
                    "year": year,
                    "language": language,
                }
            )

        return papers

    # ---------------------------------------------------------
    # LANGUAGE
    # ---------------------------------------------------------

    def filter_language(
        self,
        papers: list[dict],
        language: str,
    ) -> list[dict]:

        language_code = (
            self.LANGUAGE_CODES.get(
                language
            )
        )

        if not language_code:
            return papers

        return [
            paper
            for paper in papers
            if paper["language"].lower()
            == language_code.lower()
        ]

    # ---------------------------------------------------------
    # SIMPLE KEYWORD OVERLAP
    # ---------------------------------------------------------

    def get_keywords(
        self,
        text: str,
    ) -> set[str]:

        words = re.findall(
            r"\b[\wÀ-ÿ'-]{3,}\b",
            text.lower(),
        )

        return {
            word
            for word in words
            if word not in self.STOPWORDS
        }

    def keyword_overlap(
        self,
        claim: Claim,
        paper: dict,
    ) -> float:

        claim_words = self.get_keywords(
            claim.claim
        )

        paper_words = self.get_keywords(
            f"{paper['title']} {paper['abstract']}"
        )

        if not claim_words:
            return 0.0

        return len(
            claim_words & paper_words
        ) / len(claim_words)

    # ---------------------------------------------------------
    # RANK
    # ---------------------------------------------------------

    def rank_references(
        self,
        claim: Claim,
        papers: list[dict],
        top_k: int = 5,
    ) -> list[Reference]:

        papers = [
            paper
            for paper in papers
            if paper["title"]
            or paper["abstract"]
        ]

        if not papers:
            return []

        query_embedding = (
            self.embedder.encode(
                [claim.claim],
                convert_to_tensor=True,
            )
        )

        documents = [
            f"{paper['title']}. "
            f"{paper['abstract']}"
            for paper in papers
        ]

        document_embeddings = (
            self.embedder.encode(
                documents,
                convert_to_tensor=True,
            )
        )

        hits: list[dict[str, Any]] = (
            semantic_search(
                query_embedding,
                document_embeddings,
                top_k=len(papers),
            )[0]
        )

        ranked = []

        for hit in hits:

            paper = papers[
                int(hit["corpus_id"])
            ]

            semantic_score = float(
                hit["score"]
            )

            keyword_score = (
                self.keyword_overlap(
                    claim,
                    paper,
                )
            )

            # Semantic similarity is still the main signal.
            # Keyword overlap helps prevent papers that merely
            # share one broad medical concept from ranking too high.
            final_score = (
                0.75 * semantic_score
                + 0.25 * keyword_score
            )

            ranked.append(
                (
                    final_score,
                    semantic_score,
                    paper,
                )
            )

        ranked.sort(
            key=lambda x: x[0],
            reverse=True,
        )

        references = []

        for (
            final_score,
            semantic_score,
            paper,
        ) in ranked[:top_k]:

            references.append(
                Reference(
                    pmid=paper["pmid"],
                    title=paper["title"],
                    abstract=paper["abstract"],
                    journal=paper["journal"],
                    year=paper["year"],
                    language=paper["language"],
                    similarity=semantic_score,
                )
            )

        return references

    # ---------------------------------------------------------
    # MAIN RETRIEVAL
    # ---------------------------------------------------------

    def retrieve(
        self,
        claim: Claim,
        max_results_per_query: int = 30,
        top_k: int = 5,
        max_queries: int = 5,
    ) -> list[Reference]:

        print(
            f"\nGenerating queries for:\n"
            f"{claim.claim}"
        )

        queries = generate_queries(
            claim,
            max_queries=max_queries,
        )

        print("\nSEARCH QUERIES:")

        for i, query in enumerate(
            queries,
            1,
        ):
            print(
                f"{i}. {query}"
            )

        # -----------------------------------------------------
        # PASS 1: ARTICLE LANGUAGE
        # -----------------------------------------------------

        print(
            f"\nSearching for "
            f"{claim.language} references..."
        )

        language_pmids = (
            self.search_multiple_queries(
                queries=queries,
                language=claim.language,
                max_results_per_query=max_results_per_query,
            )
        )

        print(
            f"Language-specific PMIDs: "
            f"{len(language_pmids)}"
        )

        language_papers = (
            self.fetch_pubmed(
                language_pmids
            )
        )

        language_papers = (
            self.filter_language(
                language_papers,
                claim.language,
            )
        )

        print(
            f"Language-specific papers: "
            f"{len(language_papers)}"
        )

        language_references = (
            self.rank_references(
                claim=claim,
                papers=language_papers,
                top_k=top_k,
            )
        )

        print(
            f"Language-specific references: "
            f"{len(language_references)}"
        )

        # -----------------------------------------------------
        # If we have enough references, stop.
        # -----------------------------------------------------

        if len(language_references) >= top_k:
            return language_references

        # -----------------------------------------------------
        # PASS 2: INTERNATIONAL FALLBACK
        # -----------------------------------------------------

        print(
            "\nNot enough references in article language."
        )

        print(
            "Searching international literature..."
        )

        international_pmids = (
            self.search_multiple_queries(
                queries=queries,
                language=None,
                max_results_per_query=max_results_per_query,
            )
        )

        # Don't refetch language-specific papers.
        existing_pmids = set(
            language_pmids
        )

        international_pmids = [
            pmid
            for pmid in international_pmids
            if pmid not in existing_pmids
        ]

        print(
            f"Additional international PMIDs: "
            f"{len(international_pmids)}"
        )

        international_papers = (
            self.fetch_pubmed(
                international_pmids
            )
        )

        international_references = (
            self.rank_references(
                claim=claim,
                papers=international_papers,
                top_k=top_k,
            )
        )

        print(
            f"International references: "
            f"{len(international_references)}"
        )

        # -----------------------------------------------------
        # Prefer references in article language.
        # Fill remaining slots internationally.
        # -----------------------------------------------------

        references = list(
            language_references
        )

        existing = {
            reference.pmid
            for reference in references
        }

        for reference in international_references:

            if reference.pmid in existing:
                continue

            references.append(
                reference
            )

            existing.add(
                reference.pmid
            )

            if len(references) >= top_k:
                break

        return references
