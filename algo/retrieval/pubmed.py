from __future__ import annotations

import time
import xml.etree.ElementTree as ET

import requests

from algo.cache import Cache
from algo.models import Paper


class PubMedClient:

    def __init__(
        self,
        base_url: str,
        cache: Cache,
        email: str = "",
        api_key: str = "",
    ):
        self.base_url = base_url.rstrip("/")
        self.cache = cache
        self.email = email
        self.api_key = api_key

    # ========================================================
    # REQUEST PARAMETERS
    # ========================================================

    def _common_params(self) -> dict:
        params = {}

        if self.email:
            params["email"] = self.email

        if self.api_key:
            params["api_key"] = self.api_key

        return params

    # ========================================================
    # 4. SEARCH
    # ========================================================

    def search(
        self,
        query: str,
        language: str | None = None,
        retmax: int = 40,
    ) -> list[str]:

        params = self._common_params()

        search_query = query

        # Language-specific search.
        #
        # PubMed language terms use e.g.
        # "english[lang]"
        #
        # This is a first-pass filter.
        if language:
            search_query = (
                f"({query}) AND "
                f"{language}[lang]"
            )

        params.update({
            "db": "pubmed",
            "term": search_query,
            "retmax": retmax,
            "retmode": "json",
        })

        response = requests.get(
            f"{self.base_url}/esearch.fcgi",
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        ids = data["esearchresult"]["idlist"]

        # Be polite to NCBI.
        time.sleep(0.1)

        return ids

    # ========================================================
    # LANGUAGE + INTERNATIONAL FALLBACK
    # ========================================================

    def search_with_fallback(
        self,
        query: str,
        language: str,
        retmax: int = 40,
    ) -> list[str]:

        language_map = {
            "de": "German",
            "deu": "German",
            "german": "German",
            "en": "English",
            "eng": "English",
            "english": "English",
        }

        pubmed_language = language_map.get(
            language.lower().strip()
        )

        ids = []

        # ----------------------------------------
        # 1. Language-specific search FIRST
        # ----------------------------------------

        if pubmed_language:
            print(
                f"[PUBMED] Searching {pubmed_language} first...",
                flush=True,
            )

            ids = self.search(
                query,
                language=pubmed_language,
                retmax=retmax,
            )

            print(
                f"[PUBMED] {pubmed_language}: {len(ids)} results",
                flush=True,
            )

        # ----------------------------------------
        # 2. International fallback
        # ----------------------------------------

        if len(ids) < retmax:

            print(
                "[PUBMED] Searching international fallback...",
                flush=True,
            )

            fallback_ids = self.search(
                query,
                language=None,
                retmax=retmax,
            )

            for pmid in fallback_ids:
                if pmid not in ids:
                    ids.append(pmid)

                if len(ids) >= retmax:
                    break

        return ids

    # ========================================================
    # 5. EFETCH
    # ========================================================

    def fetch(
        self,
        pmids: list[str],
    ) -> list[Paper]:

        if not pmids:
            return []

        papers = []
        missing = []

        # ----------------------------------------------
        # Cache lookup
        # ----------------------------------------------

        for pmid in pmids:

            cached = self.cache.get_paper(
                pmid
            )

            if cached:
                papers.append(cached)
            else:
                missing.append(pmid)

        # ----------------------------------------------
        # Fetch missing papers
        # ----------------------------------------------

        if missing:

            params = self._common_params()

            params.update({
                "db": "pubmed",
                "id": ",".join(missing),
                "retmode": "xml",
            })

            response = requests.get(
                f"{self.base_url}/efetch.fcgi",
                params=params,
                timeout=60,
            )

            response.raise_for_status()

            fetched = self._parse_xml(
                response.text
            )

            for paper in fetched:
                self.cache.save_paper(
                    paper
                )
                papers.append(paper)

        # Preserve original PMID search order.
        paper_by_pmid = {
            paper.pmid: paper
            for paper in papers
        }

        return [
            paper_by_pmid[pmid]
            for pmid in pmids
            if pmid in paper_by_pmid
        ]

    # ========================================================
    # XML PARSER
    # ========================================================

    def _parse_xml(
        self,
        xml: str,
    ) -> list[Paper]:

        root = ET.fromstring(xml)

        papers = []

        for article in root.findall(
            ".//PubmedArticle"
        ):

            pmid_node = article.find(
                ".//MedlineCitation/PMID"
            )

            if pmid_node is None:
                continue

            pmid = (
                pmid_node.text or ""
            ).strip()

            # ------------------------------------------
            # Title
            # ------------------------------------------

            title_node = article.find(
                ".//ArticleTitle"
            )

            title = ""

            if title_node is not None:
                title = "".join(
                    title_node.itertext()
                ).strip()

            # ------------------------------------------
            # Abstract
            # ------------------------------------------

            abstract_parts = []

            for node in article.findall(
                ".//Abstract/AbstractText"
            ):

                text = "".join(
                    node.itertext()
                ).strip()

                label = node.attrib.get(
                    "Label"
                )

                if label:
                    text = (
                        f"{label}: {text}"
                    )

                if text:
                    abstract_parts.append(
                        text
                    )

            abstract = "\n".join(
                abstract_parts
            )

            # ------------------------------------------
            # Journal
            # ------------------------------------------

            journal_node = article.find(
                ".//Journal/Title"
            )

            journal = (
                journal_node.text.strip()
                if journal_node is not None
                and journal_node.text
                else ""
            )

            # ------------------------------------------
            # Year
            # ------------------------------------------

            year = self._extract_year(
                article
            )

            # ------------------------------------------
            # Language
            # ------------------------------------------

            language_node = article.find(
                ".//Language"
            )

            language = (
                language_node.text.strip()
                if language_node is not None
                and language_node.text
                else ""
            )

            papers.append(
                Paper(
                    pmid=pmid,
                    title=title,
                    abstract=abstract,
                    journal=journal,
                    year=year,
                    language=language,
                )
            )

        return papers

    @staticmethod
    def _extract_year(
        article: ET.Element,
    ) -> int | None:

        possible_nodes = [
            article.find(".//PubDate/Year"),
            article.find(
                ".//ArticleDate/Year"
            ),
        ]

        for node in possible_nodes:

            if node is None:
                continue

            value = (
                node.text or ""
            ).strip()

            if value.isdigit():
                return int(value)

        return None
