import os


class Settings:
    PIPELINE_VERSION = "1"

    GEMMA_MODEL = "gemma3:4b"

    PUBMED_BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    PUBMED_EMAIL = ""
    PUBMED_API_KEY = ""

    PUBMED_RESULTS_PER_QUERY = 40
    MAX_CANDIDATES = 150

    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

    CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    SEMANTIC_TOP_K = 30
    RERANK_TOP_K = 5

    CACHE_DB = "algo/cache.db"


settings = Settings()
