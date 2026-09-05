from ai.cache import (
    load_cache,
    save_cache,
)

from ai.comparer import (
    compare_claim,
)

from ai.parser import (
    parse_article,
)

from ai.claim_extractor import (
    extract_claims,
)

from ai.references_retriever import (
    ReferencesRetriever,
)


def print_results(
    claims,
    references_by_claim,
    verdicts,
):

    for i, claim in enumerate(
        claims,
        1,
    ):

        print(
            f"\n{'=' * 60}"
        )

        print(
            f"CLAIM {i}"
        )

        print(
            f"{'=' * 60}"
        )

        print(
            "Claim:",
            claim.claim,
        )

        print(
            "Language:",
            claim.language,
        )

        references = (
            references_by_claim[
                i - 1
            ]
        )

        print(
            "\nREFERENCES:"
        )

        if not references:

            print(
                "No relevant references found."
            )

        else:

            for j, reference in enumerate(
                references,
                1,
            ):

                print(
                    f"\n[{j}] "
                    f"{reference.title}"
                )

                print(
                    f"PMID: "
                    f"{reference.pmid}"
                )

                print(
                    f"Journal: "
                    f"{reference.journal}"
                )

                print(
                    f"Year: "
                    f"{reference.year}"
                )

                print(
                    f"Language: "
                    f"{reference.language}"
                )

                print(
                    f"Similarity: "
                    f"{reference.similarity:.3f}"
                )

                print(
                    f"Abstract: "
                    f"{reference.abstract[:500]}..."
                )

        verdict = verdicts[
            i - 1
        ]

        print(
            "\nVERDICT:"
        )

        print(
            verdict.verdict
        )

        print(
            "\nEXPLANATION:"
        )

        print(
            verdict.explanation
        )

        print(
            "\nREFERENCES USED:"
        )

        if not verdict.references:

            print(
                "None"
            )

        else:

            for pmid in (
                verdict.references
            ):

                print(
                    pmid
                )


def main():

    article = (
        "ai/article.txt"
    )

    text = parse_article(
        article
    )

    # ---------------------------------------------------------
    # CACHE
    # ---------------------------------------------------------

    cached = load_cache(
        text
    )

    if cached is not None:

        print(
            "CACHE HIT: using cached analysis."
        )

        claims = cached[0]
        references_by_claim = cached[1]
        verdicts = cached[2]

        print_results(
            claims,
            references_by_claim,
            verdicts,
        )

        return

    print(
        "CACHE MISS: processing article..."
    )

    # ---------------------------------------------------------
    # CLAIM EXTRACTION
    # ---------------------------------------------------------

    claims = extract_claims(
        text
    )

    # ---------------------------------------------------------
    # REFERENCE RETRIEVAL
    # ---------------------------------------------------------

    retriever = (
        ReferencesRetriever()
    )

    references_by_claim = []

    verdicts = []

    for claim in claims:

        references = (
            retriever.retrieve(
                claim=claim,
                max_results_per_query=30,
                top_k=5,
                max_queries=5,
            )
        )

        references_by_claim.append(
            references
        )

        # -----------------------------------------------------
        # VERDICT
        # -----------------------------------------------------

        verdict = compare_claim(
            claim,
            references,
        )

        verdicts.append(
            verdict
        )

    # ---------------------------------------------------------
    # CACHE
    # ---------------------------------------------------------

    save_cache(
        text,
        claims,
        references_by_claim,
        verdicts,
    )

    print(
        "\nAnalysis cached."
    )

    print_results(
        claims,
        references_by_claim,
        verdicts,
    )


if __name__ == "__main__":
    main()
