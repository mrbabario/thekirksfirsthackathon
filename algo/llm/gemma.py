from __future__ import annotations

import json
import re
from typing import Any

from ollama import chat

from algo.models import Claim, Reference


class GemmaClient:
    def __init__(self, model_name: str = "gemma3:4b"):
        self.model_name = model_name

        print(
            f"[GEMMA] Using local Ollama model: {model_name}",
            flush=True,
        )

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

    def _parse_json(self, text: str) -> dict[str, Any]:
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

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            candidate = text[start:end + 1]

            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Gemma returned invalid JSON:\n{text}"
        )

    def extract_claims(
        self,
        article: str,
    ) -> tuple[str, list[Claim]]:

        prompt = f"""
Analyze the following medical article.

Extract only atomic claims that can be medically verified
using biomedical literature.

Do not extract:
- opinions
- recommendations
- rhetorical statements
- unverifiable statements
- duplicate claims

Return ONLY valid JSON:

{{
  "language": "en",
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

ARTICLE:
{article}
"""

        data = self._parse_json(
            self._generate(
                prompt,
                max_new_tokens=1024,
            )
        )

        language = data.get("language", "en")

        claims = []

        for item in data.get("claims", []):
            claims.append(
                Claim(
                    text=item.get("text", ""),
                    subject=item.get("subject", ""),
                    predicate=item.get("predicate", ""),
                    object=item.get("object", ""),
                    entities=item.get("entities", []),
                    language=language,
                )
            )

        return language, claims

    def generate_queries(
        self,
        claim: Claim,
    ) -> list[str]:

        prompt = f"""
Generate 3 to 5 targeted PubMed search queries for this
medical claim.

Cover:
1. the core topic
2. the medical relationship/mechanism
3. important synonyms
4. population or outcome where relevant

Avoid vague queries.

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

        queries = data.get("queries", [])

        return [
            q.strip()
            for q in queries
            if isinstance(q, str) and q.strip()
        ][:5]

    def compare_claim(
        self,
        claim: Claim,
        references: list[Reference],
    ) -> dict[str, Any]:

        reference_text = []

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

        prompt = f"""
Evaluate the medical claim against the provided biomedical
references.

CLAIM:
{claim.text}

REFERENCES:

{"\n\n".join(reference_text)}

Choose exactly ONE verdict:

SUPPORTED
CONTRADICTED
MIXED
INSUFFICIENT

Rules:

- SUPPORTED: evidence generally supports the claim.
- CONTRADICTED: evidence generally conflicts with the claim.
- MIXED: evidence contains meaningful agreement and disagreement.
- INSUFFICIENT: references do not provide enough evidence.

Be careful about:
- correlation vs causation
- animal vs human studies
- observational vs randomized studies
- population differences
- dose differences
- outcome differences
- whether the paper actually addresses the claim

Return ONLY valid JSON:

{{
  "verdict": "SUPPORTED",
  "explanation": [
    {{
      "text": "The evidence shows ...",
      "references": [1, 3]
    }},
    {{
      "text": "However, the evidence is observational ...",
      "references": [3]
    }}
  ]
}}

Use ONLY reference numbers that actually exist.
DO NOT invent reference numbers.
DO NOT output PMIDs.
"""

        return self._parse_json(
            self._generate(
                prompt,
                max_new_tokens=1024,
            )
        )
