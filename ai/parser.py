from pathlib import Path
import re


def parse_article(filepath: str) -> str:
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Article not found: {path}")

    text = path.read_text(encoding="utf-8")

    text = re.sub(r"\s+", " ", text)

    return text.strip()
