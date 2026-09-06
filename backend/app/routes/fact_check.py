from dataclasses import asdict

from fastapi import APIRouter, HTTPException

from backend.app.schemas.fact_check import CheckRequest
from backend.app.services.fact_checker import check_article

router = APIRouter(tags=["fact-check"])


@router.post("/check")
def check(request: CheckRequest):
    print("\n" + "=" * 60, flush=True)
    print("[API] POST /api/check RECEIVED", flush=True)
    print("=" * 60, flush=True)

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

    if request.text:
        print(
            f"[API] Text received: {len(request.text)} characters",
            flush=True,
        )
        article = request.text

    else:
        print(
            f"[API] URL received: {request.url}",
            flush=True,
        )

        raise HTTPException(
            status_code=501,
            detail="URL extraction not implemented yet.",
        )

    try:
        print("[API] Calling algo.check_article()...", flush=True)

        result = check_article(article)

        print(
            "[API] algo.check_article() returned successfully",
            flush=True,
        )

        return asdict(result)

    except Exception as e:
        import traceback

        print("\n[API] FACT CHECK FAILED", flush=True)
        print(f"[API] {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Fact checking failed.",
        )
