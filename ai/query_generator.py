import json
import re

from ollama import chat

from ai.models import Claim


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


def generate_queries(
    claim: Claim,
    max_queries: int = 5,
) -> list[str]:

    entities = ", ".join(
        claim.entities
    )

    prompt = f"""
You are helping retrieve scientific medical references.

Generate concise search queries for PubMed that can be used
to fact-check the following medical claim.

CLAIM:
{claim.claim}

LANGUAGE:
{claim.language}

SUBJECT:
{claim.subject}

PREDICATE:
{claim.predicate}

OBJECT:
{claim.object}

ENTITIES:
{entities}

Rules:

- Generate exactly {max_queries} queries.
- Write every query in {claim.language}.
- Queries must contain concise biomedical concepts.
- Do not write complete sentences.
- Preserve the specific relationship in the claim.
- Include important population, disease, treatment,
  exposure, outcome, or location terms when relevant.
- Generate different formulations and useful synonyms.
- At least one query should investigate the proposed mechanism.
- Do not invent facts.
- Do not translate the queries into English.
- Do not include PubMed syntax such as [la], AND, OR, etc.

Return ONLY:

{{
    "queries": [
        "query 1",
        "query 2",
        "query 3",
        "query 4",
        "query 5"
    ]
}}
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
                "Gemma returned an empty response while generating queries."
            )

        try:
            data = extract_json(output)

            queries = data.get("queries")

            if not isinstance(
                queries,
                list,
            ):
                raise ValueError(
                    "Gemma did not return a queries list."
                )

            cleaned = []

            for query in queries:
                if not isinstance(
                    query,
                    str,
                ):
                    continue

                query = query.strip()

                if query:
                    cleaned.append(query)

            cleaned = list(
                dict.fromkeys(cleaned)
            )

            if not cleaned:
                raise ValueError(
                    "Gemma returned no usable queries."
                )

            return cleaned[:max_queries]

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError,
        ) as e:

            if attempt == 0:
                continue

            raise ValueError(
                f"Gemma returned invalid query JSON:\n{output}"
            ) from e

    raise RuntimeError(
        "Unexpected query generation failure."
    )
