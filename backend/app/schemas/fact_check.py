from pydantic import BaseModel


class CheckRequest(BaseModel):
    text: str | None = None
    url: str | None = None
