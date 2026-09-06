from __future__ import annotations

import requests

from algo.models import Paper


class PubMedClient:

    def __init__(
        self,
        base_url: str,
        cache,
        email: str = "",
        api_key: str = "",
    ):
        self.base_url = base_url.rstrip("/")
        self.cache = cache
        self.email = email
        self.api_key = api_key

    # ---------------------------------------------------------
    # COMMON PARAMETERS
    # ---------------------------------------------------------

    def _common_params(self) -> dict:

        params = {}

        if self.email:
            params["email"] = self.email

        if self.api_key:
            params["api_key"] = self.api_key

        return params

    # ---------------------------------------------------------
    # SEARCH
    # ---------------------------------------------------------

    def search(
        self,
        query: str,
        language: str | None = None,
        retmax: int = 40,
    ) -> list[str]:

        language_map = {
            "de": "German",
            "deu": "German",
            "german": "German",

            "en": "English",
            "eng": "English",
            "english": "English",

            "fr": "French",
            "fra": "French",
            "french": "French",

            "es": "Spanish",
            "spa": "Spanish",
            "spanish": "Spanish",

            "it": "Italian",
            "ita": "Italian",
            "italian": "Italian",

            "pt": "Portuguese",
            "por": "Portuguese",
            "portuguese": "Portuguese",
        }

        final_query = query

        if language:
            language_name = language_map.get(
                language.lower().strip(),
                language,
            )

            final_query = (
                f"({query}) AND "
                f"{language_name}[lang]"
            )

        params = {
            **self._common_params(),
            "db": "pubmed",
            "term": final_query,
            "retmax": retmax,
            "retmode": "json",
        }

        response = requests.get(
            f"{self.base_url}/esearch.fcgi",
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        return data["esearchresult"].get(
            "idlist",
            [],
        )

    # ---------------------------------------------------------
    # LANGUAGE-FIRST SEARCH
    # ---------------------------------------------------------

    def search_language_first(
        self,
        query: str,
        language: str,
        retmax: int = 40,
    ) -> tuple[list[str], list[str]]:

        language_ids = []
        international_ids = []

        # --------------------------------------------
        # 1. SEARCH TARGET LANGUAGE
        # --------------------------------------------

        print(
            f"[PUBMED] Searching language={language}",
            flush=True,
        )

        try:
            language_ids = self.search(
                query,
                language=language,
                retmax=retmax,
            )
        except Exception as e:
            print(
                f"[PUBMED] Language search failed: {e}",
                flush=True,
            )

        print(
            f"[PUBMED] {language}: "
            f"{len(language_ids)} results",
            flush=True,
        )

        # --------------------------------------------
        # 2. SEARCH INTERNATIONAL
        # --------------------------------------------

        print(
            "[PUBMED] Searching international fallback...",
            flush=True,
        )

        try:
            international_ids = self.search(
                query,
                language=None,
                retmax=retmax,
            )
        except Exception as e:
            print(
                f"[PUBMED] International search failed: {e}",
                flush=True,
            )

        print(
            f"[PUBMED] International: "
            f"{len(international_ids)} results",
            flush=True,
        )

        return language_ids, international_ids

    # ---------------------------------------------------------
    # FETCH
    # ---------------------------------------------------------

    def fetch(
        self,
        pmids: list[str],
    ) -> list[Paper]:

        if not pmids:
            return []

        cached_papers: dict[str, Paper] = {}
        missing: list[str] = []

        for pmid in pmids:

            cached = self.cache.get_paper(pmid)

            if cached is not None:
                cached_papers[pmid] = cached
            else:
                missing.append(pmid)

        fetched: list[Paper] = []

        if missing:

            params = {
                **self._common_params(),
                "db": "pubmed",
                "id": ",".join(missing),
                "retmode": "xml",
            }

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
                self.cache.save_paper(paper)

                cached_papers[
                    paper.pmid
                ] = paper

        # Preserve original PMID order.
        result = []

        for pmid in pmids:

            paper = cached_papers.get(pmid)

            if paper is not None:
                result.append(paper)

        return result

    # ---------------------------------------------------------
    # XML PARSING
    # ---------------------------------------------------------

    def _parse_xml(
        self,
        xml_text: str,
    ) -> list[Paper]:

        import xml.etree.ElementTree as ET

        root = ET.fromstring(xml_text)

        papers = []

        for article in root.findall(
            ".//PubmedArticle"
        ):

            medline = article.find(
                "./MedlineCitation"
            )

            if medline is None:
                continue

            pmid_element = medline.find(
                "./PMID"
            )

            if pmid_element is None:
                continue

            pmid = (
                pmid_element.text or ""
            ).strip()

            article_data = medline.find(
                "./Article"
            )

            if article_data is None:
                continue

            title_element = article_data.find(
                "./ArticleTitle"
            )

            title = (
                "".join(
                    title_element.itertext()
                )
                if title_element is not None
                else ""
            )

            abstract_parts = []

            for abstract_text in article_data.findall(
                "./Abstract/AbstractText"
            ):

                text = "".join(
                    abstract_text.itertext()
                )

                label = abstract_text.attrib.get(
                    "Label"
                )

                if label:
                    text = (
                        f"{label}: {text}"
                    )

                abstract_parts.append(text)

            abstract = "\n".join(
                abstract_parts
            )

            journal_element = article_data.find(
                "./Journal/Title"
            )

            journal = (
                journal_element.text or ""
                if journal_element is not None
                else ""
            )

            year = self._extract_year(
                article_data
            )

            languages = [
                (
                    element.text or ""
                ).strip()
                for element in article_data.findall(
                    "./Language"
                )
            ]

            language = (
                languages[0]
                if languages
                else ""
            )

            papers.append(
                Paper(
                    pmid=pmid,
                    title=title.strip(),
                    abstract=abstract.strip(),
                    journal=journal.strip(),
                    year=year,
                    language=language,
                )
            )

        return papers

    # ---------------------------------------------------------
    # YEAR
    # ---------------------------------------------------------

    def _extract_year(
        self,
        article_data,
    ) -> int | None:

        candidates = [
            article_data.find(
                "./Journal/JournalIssue/PubDate/Year"
            ),
            article_data.find(
                "./ArticleDate/Year"
            ),
        ]

        for element in candidates:

            if element is not None:
                value = (
                    element.text or ""
                ).strip()

                if value.isdigit():
                    return int(value)

        return None
