from ai.parser import parse_article
from ai.claim_extractor import extract_claims
from ai.references_retriever import ReferencesRetriever
from ai.comparer import compare_claim


def main():
    article = "ai/article.txt"

    text = parse_article(article)
    claims = extract_claims(text)

    retriever = ReferencesRetriever()

    for i, claim in enumerate(claims, 1):
        print(f"\n{'=' * 60}")
        print(f"CLAIM {i}")
        print(f"{'=' * 60}")

        print("Claim:", claim.claim)
        print("Language:", claim.language)

        references = retriever.retrieve(
            claim,
            top_k=3,
            min_similarity=0.55,
        )

        print("\nREFERENCES:")

        if not references:
            print("No sufficiently relevant references found.")
        else:
            for j, reference in enumerate(references, 1):
                print(f"\n[{j}] {reference.title}")
                print(f"PMID: {reference.pmid}")
                print(f"Journal: {reference.journal}")
                print(f"Year: {reference.year}")
                print(f"Language: {reference.language}")
                print(f"Similarity: {reference.similarity:.3f}")
                print(f"Abstract: {reference.abstract[:500]}...")

        verdict = compare_claim(claim, references)

        print("\nVERDICT:")
        print(verdict.verdict)

        print("\nEXPLANATION:")
        print(verdict.explanation)

        print("\nREFERENCES USED:")

        if not verdict.references:
            print("None")
        else:
            for pmid in verdict.references:
                print(pmid)


if __name__ == "__main__":
    main()
