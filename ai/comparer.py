import json
import re

from ollama import chat

from ai.models import Claim, Reference, Verdict


def extract_json(text: str) -> dict:
    text = text.strip()

    # Remove Markdown code fences if Gemma adds them.
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

    # Try parsing the entire response first.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # If there is extra text, extract the JSON object.
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"Could not find JSON object in Gemma output:\n{text}"
        )

    json_text = text[start:end + 1]

    try:
        return json.loads(json_text)
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
                "No sufficiently relevant scientific references "
                "were found to evaluate this claim."
            ),
            references=[],
        )

    reference_text = "\n\n".join(
        f"""
REFERENCE {i}:
PMID: {ref.pmid}
Title: {ref.title}
Journal: {ref.journal}
Year: {ref.year}
Abstract: {ref.abstract}
"""
        for i, ref in enumerate(references, 1)
    )

    prompt = f"""
You are a careful medical fact-checking assistant.

Determine whether the CLAIM is supported or contradicted by the
provided scientific references.

Rules:
- Do NOT use similarity to determine the verdict.
- Similarity only indicates topical relevance.
- Evaluate what the references actually say.
- Do not invent information.
- Consider qualifications, limitations, study populations, and uncertainty.
- If references disagree, use MIXED.
- If there is not enough information, use INSUFFICIENT.
- Keep the explanation concise.
- The explanation must be written in {claim.language}.
- Only cite references that actually support your reasoning.

CLAIM:
{claim.claim}

REFERENCES:
{reference_text}

Return ONLY a JSON object.

The JSON must have exactly these fields:

{{
    "verdict": "SUPPORTED",
    "explanation": "your explanation here",
    "references": ["PMID1", "PMID2"]
}}

The verdict MUST be exactly one of:
SUPPORTED
CONTRADICTED
MIXED
INSUFFICIENT

The references field MUST contain only PMIDs from the provided references.
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
                "Gemma returned an empty response after retrying."
            )

        try:
            data = extract_json(output)

            verdict = Verdict(**data)

            # Only allow PMIDs from the references given to Gemma.
            valid_pmids = {
                reference.pmid
                for reference in references
            }

            verdict.references = [
                pmid
                for pmid in verdict.references
                if pmid in valid_pmids
            ]

            return verdict

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            if attempt == 0:
                continue

            raise ValueError(
                f"Gemma returned invalid verdict:\n{output}"
            ) from e

    raise RuntimeError("Unexpected comparer failure.")
