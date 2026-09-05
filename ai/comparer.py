import json
import re

from ollama import chat

from ai.models import Claim, Reference, Verdict


def extract_json(text: str) -> dict:

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    )

    text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"Could not find JSON object in Gemma output:\n{text}"
        )

    try:
        return json.loads(
            text[start:end + 1]
        )

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemma returned invalid JSON:\n{text}"
        ) from e


def compare_claim(
    claim: Claim,
    references: list[Reference],
) -> Verdict:

    if not references:
        return Verdict(
            verdict="INSUFFICIENT",
            explanation=(
                "No relevant scientific references were found "
                "to evaluate this claim."
            ),
            references=[],
        )

    reference_text = "\n\n".join(
        f"""
REFERENCE {i}:
PMID: {ref.pmid}
Language: {ref.language}
Title: {ref.title}
Journal: {ref.journal}
Year: {ref.year}
Abstract: {ref.abstract}
"""
        for i, ref in enumerate(
            references,
            1,
        )
    )

    prompt = f"""
You are a careful medical fact-checking assistant.

Evaluate whether the CLAIM is supported, contradicted, mixed,
or not adequately established by the provided scientific references.

CLAIM LANGUAGE:
{claim.language}

CLAIM:
{claim.claim}

IMPORTANT:

1. Evaluate the actual proposition in the claim.
2. Do not require a reference to use the exact same wording.
3. Use the scientific information in the references.
4. Similarity scores are ONLY retrieval signals. Never use them
   as proof that a claim is true.
5. A reference that merely discusses the same topic is not enough.
6. If a reference provides evidence directly inconsistent with
   the claim, that supports CONTRADICTED.
7. If references directly support the claim, use SUPPORTED.
8. If some references support the claim while others contradict it,
   use MIXED.
9. If the references simply do not establish the claim either way,
   use INSUFFICIENT.
10. Do not treat "the paper does not mention the claim" as proof
    that the claim is false.
11. Consider study population, mechanism, outcome, magnitude,
    limitations, and uncertainty.
12. Do not invent facts or PMIDs.
13. The explanation must be written in {claim.language}.
14. Only cite PMIDs that actually support your explanation.

CLAIM:
{claim.claim}

REFERENCES:
{reference_text}

Return ONLY:

{{
    "verdict": "SUPPORTED",
    "explanation": "concise explanation",
    "references": ["PMID1"]
}}

The verdict MUST be exactly one of:

SUPPORTED
CONTRADICTED
MIXED
INSUFFICIENT

Definitions:

SUPPORTED:
The references provide evidence supporting the claim.

CONTRADICTED:
The references provide evidence that the claim is false,
incorrect, or inconsistent with established findings.

MIXED:
The evidence is genuinely conflicting or only partially supports
different parts of the claim.

INSUFFICIENT:
The retrieved references do not provide enough evidence to
determine the truth of the claim.
"""

    for attempt in range(2):

        response = chat(
            model="gemma4:12b",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            think=False,
            stream=False,
            options={
                "temperature": 0,
                "num_predict": 512,
            },
        )

        output = response.message.content

        if not output:

            if attempt == 0:
                continue

            raise ValueError(
                "Gemma returned an empty verdict."
            )

        try:

            data = extract_json(
                output
            )

            verdict = Verdict(
                **data
            )

            valid_pmids = {
                reference.pmid
                for reference in references
            }

            verdict.references = [
                pmid
                for pmid in verdict.references
                if pmid in valid_pmids
            ]

            if verdict.verdict not in {
                "SUPPORTED",
                "CONTRADICTED",
                "MIXED",
                "INSUFFICIENT",
            }:
                raise ValueError(
                    f"Invalid verdict: "
                    f"{verdict.verdict}"
                )

            return verdict

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError,
        ) as e:

            if attempt == 0:
                continue

            raise ValueError(
                f"Gemma returned invalid verdict:\n{output}"
            ) from e

    raise RuntimeError(
        "Unexpected comparer failure."
    )
