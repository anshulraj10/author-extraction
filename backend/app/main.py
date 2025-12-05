"""Minimal FastAPI app for receiving text and returning author metadata."""

from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    """Request body for extracting author names."""

    text: str = Field(..., description="Free-form text containing author names.")


class ExtractResponse(BaseModel):
    """Response payload describing detected authors."""

    authors: List[str]


app = FastAPI(
    title="Author Extraction API",
    version="0.1.0",
    description="Prototype service that identifies authors from submitted text.",
)


@app.get("/health", tags=["core"])
async def health_check():
    """Simple health probe used by orchestrators."""

    return {"status": "ok"}


@app.post("/extract", response_model=ExtractResponse, tags=["extract"])
async def extract_authors(payload: ExtractRequest):
    """Stub endpoint that echoes an empty author list until extraction logic is implemented."""

    # TODO: replace with actual NLP or heuristic-based extraction logic.
    return ExtractResponse(authors=[])
