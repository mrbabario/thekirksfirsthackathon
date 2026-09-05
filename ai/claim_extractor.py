import json
import re

from langdetect import detect
from ollama import chat

from ai.models import Claim


LANGUAGE_NAMES = {
    "en": "English",
    "ms": "Malay",
    "zh-cn": "Chinese",
    "zh-tw": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "pt": "Portuguese",
    "it": "Italian",
    "ru": "Russian",
}


def detect_language(text: str) -> str:
    code = detect(text)

    return LANGUAGE_NAMES.get(
        code,
        code,
    )


def extract_json(text: str) -> list[dict]:
    text = text.strip()

    # Remove Markdown code fences.
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
        data = json.loads(text)

        if not isinstance(data, list):
            raise ValueError(
                "Gemma returned JSON, but it was not a JSON array."
            )

        return data

    except json.JSONDecodeError:
        pass

    # If Gemma added extra text, extract the JSON array.
    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"Could not find JSON array in model output:\n{text}"
        )

    json_text = text[start:end + 1]

    try:
        data = json.loads(
            json_text
        )

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Gemma returned invalid JSON:\n{text}"
        ) from e

    if not isinstance(data, list):
        raise ValueError(
            "Gemma returned JSON, but it was not a JSON array."
        )

    return data


def extract_claims(
    article_text: str,
) -> list[Claim]:

    language = detect_language(
        article_text
    )

    prompt = f"""
You are a medical fact-checking assistant.

The article language has already been detected as:
{language}

Extract factual, medically verifiable claims from the article.

IMPORTANT:
- Every claim MUST be written in {language}.
- Do NOT translate claims into another language.
- Do NOT invent claims.
- Do NOT add information that is not stated in the article.
- Preserve medical terminology accurately.
- Break compound statements into separate atomic claims.

Only extract claims that can be checked against scientific
or medical literature.

Do NOT extract:
- opinions
- questions
- anecdotes
- advertisements
- rhetorical statements
- purely descriptive statements

Return ONLY a JSON array.

Each object must contain:

claim:
    A clear atomic factual claim written in {language}.

language:
    "{language}"

entities:
    Important medical entities mentioned in the claim.

subject:
    Subject of the claim.

predicate:
    Relationship or action.

object:
    Object of the relationship.

ARTICLE:

{article_text}
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
                "num_predict": 1024,
            },
        )

        output = response.message.content

        if not output:

            if attempt == 0:
                continue

            raise ValueError(
                "Gemma returned an empty response "
                "while extracting claims."
            )

        try:

            data = extract_json(
                output
            )

            claims = []

            for item in data:

                item["language"] = language

                claims.append(
                    Claim(
                        **item
                    )
                )

            # -------------------------------------------------
            # CONSOLE OUTPUT
            # -------------------------------------------------

            print(
                "\n"
                + "=" * 60
            )

            print(
                "CLAIM EXTRACTION"
            )

            print(
                "=" * 60
            )

            print(
                f"Detected language: {language}"
            )

            print(
                f"Claims found: {len(claims)}"
            )

            for i, claim in enumerate(
                claims,
                1,
            ):

                print(
                    f"\n[{i}] {claim.claim}"
                )

                print(
                    f"    Language: "
                    f"{claim.language}"
                )

                print(
                    f"    Entities: "
                    f"{', '.join(claim.entities)}"
                )

                print(
                    f"    Subject: "
                    f"{claim.subject}"
                )

                print(
                    f"    Predicate: "
                    f"{claim.predicate}"
                )

                print(
                    f"    Object: "
                    f"{claim.object}"
                )

            print(
                "=" * 60
            )

            return claims

        except (
            json.JSONDecodeError,
            ValueError,
            TypeError,
        ) as e:

            if attempt == 0:
                continue

            raise ValueError(
                f"Gemma returned invalid claim JSON:\n{output}"
            ) from e

    raise RuntimeError(
        "Unexpected claim extraction failure."
    )
