"""Minimal FastAPI app for receiving text and returning author metadata."""

from datetime import datetime
import shutil
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from backend.app.config import CACHE_DIR, DEFAULT_MODEL_ID, MODEL_IDS
from backend.app.process import process_references
from backend.app.utils import run_health_check


app = FastAPI(
    title="Author Extraction API",
    version="0.1.0",
    description="Prototype service that identifies authors from submitted text.",
)


@app.get("/health", tags=["core"])
async def health_check():
    """Simple health probe used by orchestrators."""

    connections = run_health_check()
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "services": [
            {
                "name": "Grobid",
                "connected": connections["gorbid_connection"],
                "message": connections["gorbid_message"],
            },
            {
                "name": "Gemini",
                "connected": connections["gemini_connection"],
                "message": connections["gemini_message"],
            },
        ],
    }


@app.get("/models", tags=["core"])
async def available_models():
    """Expose available Gemini models for the UI dropdown."""

    return {"models": MODEL_IDS, "default": DEFAULT_MODEL_ID}


@app.get("/")
async def root():
    return {"message": "Hello World!"}


@app.post("/process-pdf")
async def process_pdf(
    file: UploadFile = File(...),
    model_id: str = Form(DEFAULT_MODEL_ID),
):
    """
    Endpoint to accept a PDF file and save it to the local cache folder.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDFs are allowed.")
    
    PDF_DIR = CACHE_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    if model_id not in MODEL_IDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model_id; pick one of {MODEL_IDS}.",
        )

    file_location = PDF_DIR / file.filename

    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    finally:
        file.file.close()
        
    try:
        response = process_references(PDF_DIR, file.filename, model_id=model_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Data extraction failed: {str(e)}",
        ) from e

    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
