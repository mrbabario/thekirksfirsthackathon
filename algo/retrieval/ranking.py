from __future__ import annotations

import numpy as np
from sentence_transformers import (
    CrossEncoder,
    SentenceTransformer,
)

from algo.models import Claim, Paper


class Ranker:

    def __init__(
        self,
        embedding_model_name: str,
        cross_encoder_model_name: str,
    ):
        self.embedding_model = (
            SentenceTransformer(
                embedding_model_name
            )
        )

        self.cross_encoder = CrossEncoder(
            cross_encoder_model_name
        )

    # ========================================================
    # 6. FIRST-STAGE SEMANTIC RETRIEVAL
    # ========================================================

    def semantic_retrieve(
        self,
        claim: Claim,
        papers: list[Paper],
        top_k: int,
    ) -> list[Paper]:

        if not papers:
            return []

        claim_embedding = (
            self.embedding_model.encode(
                claim.text,
                normalize_embeddings=True,
            )
        )

        documents = [
            self._paper_text(paper)
            for paper in papers
        ]

        paper_embeddings = (
            self.embedding_model.encode(
                documents,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
        )

        # Since both embeddings are normalized,
        # dot product = cosine similarity.
        scores = np.dot(
            paper_embeddings,
            claim_embedding,
        )

        top_k = min(
            top_k,
            len(papers),
        )

        indices = np.argsort(
            scores
        )[::-1][:top_k]

        return [
            papers[i]
            for i in indices
        ]

    # ========================================================
    # 7. CROSS-ENCODER RERANKING
    # ========================================================

    def rerank(
        self,
        claim: Claim,
        papers: list[Paper],
        top_k: int,
    ) -> list[Paper]:

        if not papers:
            return []

        pairs = [
            (
                claim.text,
                self._paper_text(paper),
            )
            for paper in papers
        ]

        scores = self.cross_encoder.predict(
            pairs
        )

        top_k = min(
            top_k,
            len(papers),
        )

        indices = np.argsort(
            scores
        )[::-1][:top_k]

        return [
            papers[i]
            for i in indices
        ]

    # ========================================================
    # PAPER TEXT
    # ========================================================

    @staticmethod
    def _paper_text(
        paper: Paper,
    ) -> str:

        return (
            f"{paper.title}\n\n"
            f"{paper.abstract}"
        )
