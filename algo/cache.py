from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
from dataclasses import asdict

from algo.models import (
    ArticleResult,
    Claim,
    ClaimResult,
    ExplanationPart,
    Paper,
    Reference,
)


class Cache:
    def __init__(self, db_path: str):
        parent = os.path.dirname(db_path)

        if parent:
            os.makedirs(parent, exist_ok=True)

        self.conn = sqlite3.connect(
            db_path,
            check_same_thread=False,
        )

        self._create_tables()

    # ========================================================
    # DATABASE
    # ========================================================

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS article_cache (
                article_hash TEXT NOT NULL,
                pipeline_version TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at REAL NOT NULL,

                PRIMARY KEY (
                    article_hash,
                    pipeline_version
                )
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS paper_cache (
                pmid TEXT PRIMARY KEY,
                paper_json TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)

        self.conn.commit()

    # ========================================================
    # ARTICLE CACHE
    # ========================================================

    def get_article(
        self,
        article_hash: str,
        pipeline_version: str,
    ) -> ArticleResult | None:

        row = self.conn.execute(
            """
            SELECT result_json
            FROM article_cache
            WHERE article_hash = ?
              AND pipeline_version = ?
            """,
            (
                article_hash,
                pipeline_version,
            ),
        ).fetchone()

        if row is None:
            return None

        data = json.loads(row[0])

        claim_results = []

        for item in data["claims"]:
            claim = Claim(**item["claim"])

            explanation = [
                ExplanationPart(**part)
                for part in item["explanation"]
            ]

            references = [
                Reference(**ref)
                for ref in item["references"]
            ]

            claim_results.append(
                ClaimResult(
                    claim=claim,
                    verdict=item["verdict"],
                    explanation=explanation,
                    references=references,
                )
            )

        return ArticleResult(
            article_hash=data["article_hash"],
            language=data["language"],
            claims=claim_results,
        )

    def save_article(
        self,
        result: ArticleResult,
        pipeline_version: str,
    ):
        self.conn.execute(
            """
            INSERT OR REPLACE INTO article_cache
            (
                article_hash,
                pipeline_version,
                result_json,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                result.article_hash,
                pipeline_version,
                json.dumps(
                    asdict(result),
                    ensure_ascii=False,
                ),
                time.time(),
            ),
        )

        self.conn.commit()

    # ========================================================
    # PAPER CACHE
    # ========================================================

    def get_paper(
        self,
        pmid: str,
    ) -> Paper | None:

        row = self.conn.execute(
            """
            SELECT paper_json
            FROM paper_cache
            WHERE pmid = ?
            """,
            (pmid,),
        ).fetchone()

        if row is None:
            return None

        return Paper(
            **json.loads(row[0])
        )

    def save_paper(
        self,
        paper: Paper,
    ):
        self.conn.execute(
            """
            INSERT OR REPLACE INTO paper_cache
            (
                pmid,
                paper_json,
                created_at
            )
            VALUES (?, ?, ?)
            """,
            (
                paper.pmid,
                json.dumps(
                    asdict(paper),
                    ensure_ascii=False,
                ),
                time.time(),
            ),
        )

        self.conn.commit()

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self):
        self.conn.close()


def article_hash(text: str) -> str:
    """
    Produce a deterministic hash for an article.

    Formatting differences such as repeated whitespace
    do not create different cache entries.
    """

    normalized = " ".join(
        text.strip().split()
    ).lower()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()
