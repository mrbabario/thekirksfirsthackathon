from typing import Any
import requests
import xml.etree.ElementTree as ET

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import semantic_search

from ai.models import Claim, Reference


class ReferencesRetriever:
    PUBMED_URL = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    )

    def __init__(self):
        self.embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        )

    def search_pubmed(
        self,
        query: str,
        max_results: int = 20,
    ) -> list[str]:

        params = {
            "db": "pubmed",
            "term": query,
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

        return response.json()["esearchresult"]["idlist"]

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

        root = ET.fromstring(response.text)

        papers = []

        for article in root.findall(".//PubmedArticle"):
            pmid = article.findtext(".//PMID", default="")
            title = article.findtext(".//ArticleTitle", default="")

            abstract_parts = []

            for part in article.findall(
                ".//Abstract/AbstractText"
            ):
                text = "".join(part.itertext()).strip()

                if text:
                    abstract_parts.append(text)

            abstract = " ".join(abstract_parts)

            journal = article.findtext(
                ".//Journal/Title",
                default=""
            )

            year = ""

            year_node = article.find(".//PubDate/Year")

            if year_node is not None:
                year = year_node.text or ""

            languages = [
                node.text
                for node in article.findall(".//Language")
                if node.text
            ]

            language = languages[0] if languages else "unknown"

            papers.append({
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "year": year,
                "language": language,
            })

        return papers

    def rank_references(
        self,
        claim: Claim,
        papers: list[dict],
        top_k: int = 3,
        min_similarity: float = 0.55,
    ) -> list[Reference]:

        papers = [
            paper
            for paper in papers
            if paper["title"] or paper["abstract"]
        ]

        if not papers:
            return []

        query_embedding = self.embedder.encode(
            [claim.claim],
            convert_to_tensor=True,
        )

        documents = [
            f"{paper['title']}. {paper['abstract']}"
            for paper in papers
        ]

        document_embeddings = self.embedder.encode(
            documents,
            convert_to_tensor=True,
        )

        hits: list[dict[str, Any]] = semantic_search(
            query_embedding,
            document_embeddings,
            top_k=len(papers),
        )[0]

        references = []

        for hit in hits:
            similarity = float(hit["score"])

            if similarity < min_similarity:
                break

            paper = papers[int(hit["corpus_id"])]

            references.append(
                Reference(
                    pmid=paper["pmid"],
                    title=paper["title"],
                    abstract=paper["abstract"],
                    journal=paper["journal"],
                    year=paper["year"],
                    language=paper["language"],
                    similarity=similarity,
                )
            )

            if len(references) == top_k:
                break

        return references

    def retrieve(
        self,
        claim: Claim,
        max_results: int = 20,
        top_k: int = 3,
        min_similarity: float = 0.55,
    ) -> list[Reference]:

        pmids = self.search_pubmed(
            claim.claim,
            max_results=max_results,
        )

        papers = self.fetch_pubmed(pmids)

        return self.rank_references(
            claim,
            papers,
            top_k=top_k,
            min_similarity=min_similarity,
        )
