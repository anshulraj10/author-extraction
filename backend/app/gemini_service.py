import os
import json
import time
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

from backend.app.config import MODEL_IDS, DEFAULT_MODEL_ID

# Load environment variables
load_dotenv()

# Initialize the client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

BATCH_SIZE = 5

def enrich_references_with_gemini(
    references: List[Dict[str, Any]],
    model_id: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Takes a list of cleaned references and uses Gemini with Google Search
    to find author emails and affiliations.
    """
    enriched_results = []
    
    selected_model = model_id or DEFAULT_MODEL_ID
    if selected_model not in MODEL_IDS:
        selected_model = DEFAULT_MODEL_ID

    print(f"Starting enrichment for {len(references)} references using {selected_model}...")
    
    for i in range(0, len(references), BATCH_SIZE):
        batch = references[i : i + BATCH_SIZE]
        print(f"Processing batch {i} to {i + len(batch)}...")
        
        try:
            batch_result = _process_batch(batch, selected_model)
            enriched_results.extend(batch_result)
        except Exception as e:
            print(f"Error processing batch {i}: {e}")
            enriched_results.extend(batch)
            
        time.sleep(2)

    return enriched_results

def _process_batch(
    batch: List[Dict[str, Any]], selected_model: str
) -> List[Dict[str, Any]]:
    """
    Helper function to send a specific batch to Gemini.
    """
    
    # 1. Prompt Update
    prompt = f"""
    You are a research assistant. I will provide a list of academic references where the 'authors' field contains a list of objects with null fields.
    
    Your task for EACH author in the 'authors' list:
    1. Use Google Search to find their **current affiliation** (university or company).
    2. Use Google Search to find their **public academic/professional email address**.
    3. Use Google Search to find a relevant **website**.
    4. If info is not found, leave as null.
    
    Input Data:
    {json.dumps(batch, indent=2)}
    
    **IMPORTANT OUTPUT FORMAT:**
    Return ONLY a raw JSON list. Do not include any explanations, preambles, or markdown formatting other than the JSON block.
    """

    # 2. Safety Settings: CRITICAL for extracting names/emails
    # We must explicitly disable blocking to allow searching for people.
    safety_settings = [
        types.SafetySetting(
            category="HARM_CATEGORY_HATE_SPEECH",
            threshold="BLOCK_NONE",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_DANGEROUS_CONTENT",
            threshold="BLOCK_NONE",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_HARASSMENT",
            threshold="BLOCK_NONE",
        ),
        types.SafetySetting(
            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
            threshold="BLOCK_NONE",
        ),
    ]

    # 3. Call Gemini
    response = client.models.generate_content(
        model=selected_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            safety_settings=safety_settings,
            # response_mime_type="application/json" # Removed to allow Tool use
        )
    )

    # 4. Robust Parsing & Debugging
    try:
        # Check if we have candidates
        if not response.candidates:
            print("Error: No candidates returned.")
            return batch

        candidate = response.candidates[0]
        
        # Check why it finished
        if candidate.finish_reason != "STOP":
            print(f"Warning: Model stopped unexpectedly. Reason: {candidate.finish_reason}")
            # If safety filter triggered despite settings, it will show here
            
        text_response = response.text
        if not text_response:
            print("Error: Empty text response from Gemini (possibly filtered).")
            # print(candidate) # Uncomment to debug raw candidate
            return batch

        # Clean Markdown Code Blocks
        json_match = re.search(r'(\[.*\])', text_response, re.DOTALL)
        
        if json_match:
            clean_json = json_match.group(1)
            result_json = json.loads(clean_json)
            return result_json
        else:
            return json.loads(text_response)

    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON. Error: {e}")
        return batch
    except Exception as e:
        print(f"Unexpected error: {e}")
        return batch
