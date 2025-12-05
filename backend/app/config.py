import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / "cache"
DEFAULT_GROBID_CONFIG = BASE_DIR / "grobid-config.json"
_env_config_path = os.environ.get("GROBID_CONFIG_PATH")

if _env_config_path:
    _candidate_path = Path(_env_config_path)
    GROBID_CONFIG_PATH = _candidate_path if _candidate_path.exists() else DEFAULT_GROBID_CONFIG
else:
    GROBID_CONFIG_PATH = DEFAULT_GROBID_CONFIG

SAMPLE_RESULTS_PATH = CACHE_DIR / "temp.json"
AUTHOR_LIMIT_PER_PAPER = 5
MODEL_IDS = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro-preview"]
DEFAULT_MODEL_ID = MODEL_IDS[1] if len(MODEL_IDS) > 1 else MODEL_IDS[0]
