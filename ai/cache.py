import hashlib
import json
from pathlib import Path

from ai.models import Claim, Reference, Verdict


CACHE_DIR = Path("cache")

CACHE_VERSION = 5


def get_article_hash(
    article_text: str,
) -> str:

    return hashlib.sha256(
        article_text.encode("utf-8")
    ).hexdigest()


def get_cache_path(
    article_text: str,
) -> Path:

    return (
        CACHE_DIR
        / f"{get_article_hash(article_text)}.json"
    )


def load_cache(
    article_text: str,
) -> tuple[
    list[Claim],
    list[list[Reference]],
    list[Verdict],
] | None:

    path = get_cache_path(
        article_text
    )

    if not path.exists():
        return None

    try:

        data = json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

        if data.get(
            "version"
        ) != CACHE_VERSION:
            return None

        claims = [
            Claim(**claim)
            for claim in data["claims"]
        ]

        references = [
            [
                Reference(**reference)
                for reference in claim_references
            ]
            for claim_references in data[
                "references"
            ]
        ]

        verdicts = [
            Verdict(**verdict)
            for verdict in data["verdicts"]
        ]

        return (
            claims,
            references,
            verdicts,
        )

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError,
    ):
        return None


def save_cache(
    article_text: str,
    claims: list[Claim],
    references: list[list[Reference]],
    verdicts: list[Verdict],
) -> None:

    CACHE_DIR.mkdir(
        exist_ok=True
    )

    path = get_cache_path(
        article_text
    )

    data = {
        "version": CACHE_VERSION,

        "article_hash": get_article_hash(
            article_text
        ),

        "claims": [
            claim.model_dump()
            for claim in claims
        ],

        "references": [
            [
                reference.model_dump()
                for reference in claim_references
            ]
            for claim_references in references
        ],

        "verdicts": [
            verdict.model_dump()
            for verdict in verdicts
        ],
    }

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def clear_cache() -> None:

    if not CACHE_DIR.exists():
        return

    for path in CACHE_DIR.glob(
        "*.json"
    ):
        path.unlink()
