from __future__ import annotations

import json
import re
from typing import Any

from ollama import chat

from algo.models import Claim, Reference


class GemmaClient:
    def __init__(
        self,
        model_name: str = "gemma3:4b",
    ):
        self.model_name = model_name

        print(
            f"[GEMMA] Using local Ollama model: {model_name}",
            flush=True,
        )

    # ---------------------------------------------------------
    # GENERATION
    # ---------------------------------------------------------

    def _generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
    ) -> str:

        print(
            f"[GEMMA] Sending {len(prompt)} prompt characters...",
            flush=True,
        )

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
                "num_predict": max_new_tokens,
            },
        )

        text = response["message"]["content"]

        print(
            f"[GEMMA] Received {len(text)} response characters.",
            flush=True,
        )

        return text.strip()

    # ---------------------------------------------------------
    # JSON PARSING
    # ---------------------------------------------------------

    def _parse_json(
        self,
        text: str,
    ) -> dict[str, Any]:

        text = text.strip()

        # Remove markdown fences.
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

        # Try direct JSON.
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting outer JSON object.
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1 and end > start:
            candidate = text[start:end + 1]

            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Gemma returned invalid JSON:\n{text}"
        )

    # ---------------------------------------------------------
    # LANGUAGE + CLAIM EXTRACTION
    # ---------------------------------------------------------

    def extract_claims(
        self,
        article: str,
    ) -> tuple[str, list[Claim]]:

        prompt = f"""
Analyze the following medical article.

First identify the language of the ORIGINAL ARTICLE.

Use an ISO 639-1 language code:
German -> "de"
English -> "en"
French -> "fr"
Spanish -> "es"
etc.

Then extract only atomic claims that can be medically
verified using biomedical literature.

Do not extract:
- opinions
- recommendations
- rhetorical statements
- unverifiable statements
- duplicate claims

The claim text should remain in the ORIGINAL LANGUAGE
of the article.

Return ONLY valid JSON in exactly this format:

{{
  "language": "de",
  "claims": [
    {{
      "text": "...",
      "subject": "...",
      "predicate": "...",
      "object": "...",
      "entities": ["..."]
    }}
  ]
}}

ORIGINAL ARTICLE:
{article}
"""

        data = self._parse_json(
            self._generate(
                prompt,
                max_new_tokens=1024,
            )
        )

        language = str(
            data.get("language", "en")
        ).lower().strip()

        claims: list[Claim] = []

        for item in data.get("claims", []):

            if not isinstance(item, dict):
                continue

            text = item.get("text", "")

            if not isinstance(text, str):
                continue

            if not text.strip():
                continue

            claims.append(
                Claim(
                    text=text.strip(),
                    subject=str(
                        item.get("subject", "")
                    ),
                    predicate=str(
                        item.get("predicate", "")
                    ),
                    object=str(
                        item.get("object", "")
                    ),
                    entities=[
                        str(x)
                        for x in item.get(
                            "entities",
                            [],
                        )
                    ],
                    language=language,
                )
            )

        return language, claims

    # ---------------------------------------------------------
    # PUBMED QUERY GENERATION
    # ---------------------------------------------------------

    def generate_queries(
        self,
        claim: Claim,
    ) -> list[str]:

        prompt = f"""
Generate 3 to 5 targeted PubMed search queries for this
medical claim.

The search queries should be suitable for PubMed.

Cover:
1. the core topic
2. the medical relationship or mechanism
3. important synonyms
4. population or outcome where relevant

Prefer medically precise terminology.

The claim is written in language:
{claim.language}

You may use internationally recognized medical terminology
such as English MeSH terms where useful.

Return ONLY valid JSON:

{{
  "queries": [
    "query 1",
    "query 2",
    "query 3"
  ]
}}

CLAIM:
{claim.text}

SUBJECT:
{claim.subject}

PREDICATE:
{claim.predicate}

OBJECT:
{claim.object}

ENTITIES:
{", ".join(claim.entities)}
"""

        data = self._parse_json(
            self._generate(
                prompt,
                max_new_tokens=512,
            )
        )

        queries = data.get(
            "queries",
            [],
        )

        if not isinstance(queries, list):
            return []

        return [
            q.strip()
            for q in queries
            if isinstance(q, str)
            and q.strip()
        ][:5]

    # ---------------------------------------------------------
    # CLAIM COMPARISON
    # ---------------------------------------------------------

    def compare_claim(
        self,
        claim: Claim,
        references: list[Reference],
    ) -> dict[str, Any]:

        reference_text: list[str] = []

        for ref in references:

            reference_text.append(
                f"""
[{ref.number}]
Title: {ref.title}
Journal: {ref.journal}
Year: {ref.year}
Abstract:
{ref.abstract}
""".strip()
            )

        output_language = claim.language

        prompt = f"""
Evaluate this medical claim against the provided
biomedical references.

CLAIM:
{claim.text}

ORIGINAL ARTICLE LANGUAGE:
{output_language}

REFERENCES:

{"\n\n".join(reference_text)}

Choose exactly ONE verdict:

SUPPORTED
CONTRADICTED
MIXED
INSUFFICIENT

Rules:

- SUPPORTED:
  Evidence generally supports the claim.

- CONTRADICTED:
  Evidence generally conflicts with the claim.

- MIXED:
  Evidence contains meaningful agreement and disagreement.

- INSUFFICIENT:
  The references do not provide enough evidence.

Be careful about:

- correlation vs causation
- animal vs human studies
- observational vs randomized studies
- population differences
- dose differences
- outcome differences
- whether the paper actually addresses the claim

IMPORTANT LANGUAGE RULE:

Write the explanation in the SAME LANGUAGE as the
original article.

Original article language:
{output_language}

For example:

de -> write the explanation in German.
en -> write the explanation in English.
fr -> write the explanation in French.

Do NOT translate reference titles or abstracts.

Every explanation part must explicitly cite the numbered
references that support that statement.

Use ONLY reference numbers that actually exist.

DO NOT invent reference numbers.
DO NOT output PMIDs.

Return ONLY valid JSON:

{{
  "verdict": "SUPPORTED",
  "explanation": [
    {{
      "text": "...",
      "references": [1, 3]
    }},
    {{
      "text": "...",
      "references": [3]
    }}
  ]
}}
"""

        return self._parse_json(
            self._generate(
                prompt,
                max_new_tokens=1024,
            )
        )
