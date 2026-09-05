import json

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

    return LANGUAGE_NAMES.get(code, code)


def extract_json(text: str) -> list[dict]:
    start = text.find("[")
    end = text.rfind("]")

    if start == -1 or end == -1:
        raise ValueError(
            f"Could not find JSON array in model output:\n{text}"
        )

    return json.loads(text[start:end + 1])


def extract_claims(article_text: str) -> list[Claim]:
    language = detect_language(article_text)

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

    response = chat(
        model="gemma4:12b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    output = response.message.content

    if output is None:
        raise ValueError("LLM returned no output")

    data = extract_json(output)

    claims = []

    for item in data:
        # Never trust the model's language field.
        item["language"] = language

        claims.append(
            Claim(**item)
        )

    return claims
