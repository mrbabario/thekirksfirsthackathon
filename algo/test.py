from __future__ import annotations

import json
import sys
from dataclasses import asdict

from algo.config import settings
from algo.pipeline import FactChecker


def main():
    # Default input file.
    filename = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "article.txt"
    )

    # --------------------------------------------------------
    # Read article
    # --------------------------------------------------------

    try:
        with open(
            filename,
            "r",
            encoding="utf-8",
        ) as f:
            article = f.read()

    except FileNotFoundError:
        print(
            f"Error: {filename} not found."
        )
        sys.exit(1)

    if not article.strip():
        print(
            f"Error: {filename} is empty."
        )
        sys.exit(1)

    # --------------------------------------------------------
    # Run fact checker
    # --------------------------------------------------------

    checker = FactChecker(settings)

    result = checker.check_article(article)

    # --------------------------------------------------------
    # Print JSON result
    # --------------------------------------------------------

    print(
        json.dumps(
            asdict(result),
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
