import json

from backend.app.gemini_service import enrich_references_with_gemini
from backend.app.grobid import get_data_from_gorbid
from backend.app.utils import parse_grobid_json
from backend.app.config import DEFAULT_MODEL_ID, MODEL_IDS


def process_references(pdf_dir, pdf_filename, model_id: str = DEFAULT_MODEL_ID):
    json_file = pdf_dir / get_data_from_gorbid(pdf_dir)
    with open(json_file, "r", encoding="utf-8") as file:
        grobid_json_data = json.load(file)

    gemini_input_json = parse_grobid_json(grobid_json_data)

    selected_model = model_id if model_id in MODEL_IDS else DEFAULT_MODEL_ID
    gemini_response = enrich_references_with_gemini(
        gemini_input_json, model_id=selected_model
    )

    return gemini_response
