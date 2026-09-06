from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from backend.app.schemas.fact_check import CheckRequest
from backend.app.services.fact_checker import check_article


router = APIRouter(
    prefix="/api",
    tags=["fact-check"],
)


@router.post("/check")
def check(request: CheckRequest):

    if request.text and request.url:
        raise HTTPException(
            status_code=400,
            detail="Provide either text or URL, not both.",
        )

    if not request.text and not request.url:
        raise HTTPException(
            status_code=400,
            detail="Provide article text or URL.",
        )

    # For now, start with pasted text.
    # URL extraction can be added here afterward.
    if request.text:
        article = request.text

    else:
        raise HTTPException(
            status_code=501,
            detail="URL extraction not implemented yet.",
        )

    try:
        result = check_article(article)

    except Exception as e:
        print(f"[FACT CHECK ERROR] {e}", flush=True)

        raise HTTPException(
            status_code=500,
            detail="Fact checking failed.",
        )

    return asdict(result)
