import os
from typing import List, Dict, Any
from google import genai
from backend.app.config import AUTHOR_LIMIT_PER_PAPER
from grobid_client.grobid_client import GrobidClient
from backend.app.config import GROBID_CONFIG_PATH

def parse_grobid_json(grobid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parses raw GROBID JSON output into a cleaner format optimized for 
    Gemini search and contact extraction.
    
    Args:
        grobid_data: The raw JSON dictionary output from GROBID.
        
    Returns:
        A list of cleaned reference dictionaries where authors are objects.
    """
    cleaned_references = []
    
    # We focus strictly on the 'references' list as requested
    raw_references = grobid_data.get("references", [])
    
    for ref in raw_references:
        # --- 1. Author Handling ---
        # Handle both list of strings and single string (group authors)
        raw_authors = ref.get("authors", [])
        author_names = []
        
        if isinstance(raw_authors, str):
            # Case: "Deepseek-Ai" or "Qwen Team"
            author_names = [raw_authors]
        elif isinstance(raw_authors, list):
            # Case: ["Author A", "Author B", ...]
            # Filter out empty strings
            valid_authors = [a for a in raw_authors if a]
            author_names = valid_authors[:AUTHOR_LIMIT_PER_PAPER]
            
        # TRANSFORM: Convert strings to structured objects immediately
        # This creates the "template" for Gemini to fill in
        final_authors = []
        for name in author_names:
            final_authors.append({
                "name": name,
                "affiliation": None,
                "email": None,
                "website": None
            })
        
        # --- 2. Journal Waterfall Logic ---
        # Determine the best venue name for search context
        journal = ref.get("journal")
        
        if not journal:
            # Fallback 1: Report Type (e.g., "arXiv preprint")
            journal = ref.get("note_report_type")
            
        if not journal and ref.get("arxiv"):
            # Fallback 2: If no journal name but has ArXiv ID, implies ArXiv
            journal = "arXiv"
            
        if not journal:
            # Fallback 3: Publisher (e.g., "NeurIPS")
            journal = ref.get("publisher")
            
        # --- 3. Construct "Notes" (Search Context) ---
        # Combine high-value identifiers into a single context string for Gemini
        notes_parts = []
        
        if ref.get("arxiv"):
            notes_parts.append(f"ArXiv ID: {ref['arxiv']}")
            
        if ref.get("urls"):
            # URLs can be a list or string in raw data, ensure it's a string
            urls = ref["urls"]
            if isinstance(urls, list):
                # Take the first URL if it's a list
                if urls:
                    notes_parts.append(f"URL: {urls[0]}")
            else:
                notes_parts.append(f"URL: {urls}")
                
        if ref.get("doi"):
            notes_parts.append(f"DOI: {ref['doi']}")
            
        if ref.get("volume"):
            notes_parts.append(f"Vol: {ref['volume']}")
            
        if ref.get("year"):
             notes_parts.append(f"Year: {ref['year']}")

        # Join parts with a separator
        notes_str = " | ".join(notes_parts)

        # --- 4. Build Final Object ---
        cleaned_entry = {
            "title": ref.get("title", "Unknown Title"),
            "year": ref.get("year") or ref.get("publication_date"),
            "authors": final_authors, # Now a list of objects: [{"name": "...", "email": null}, ...]
            "journal": journal if journal else "Unknown Venue",
            "notes": notes_str
        }
        
        cleaned_references.append(cleaned_entry)
        
    return cleaned_references


def run_health_check():
    try:
        client = GrobidClient(config_path=GROBID_CONFIG_PATH)
        gorbid_connection = True
        gorbid_message = "Successful!"
    except Exception as e:
        gorbid_connection = False
        gorbid_message = f"Unsuccessful! Error: {e}"
        
    try:
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        gemini_connection = True
        gemini_message = "Successful!"
    except Exception as e:
        gemini_connection = False
        gemini_message = f"Unsuccessful! Error: {e}"
        
    return {
        "gorbid_connection": gorbid_connection,
        "gorbid_message": gorbid_message,
        "gemini_connection": gemini_connection,
        "gemini_message": gemini_message
    }