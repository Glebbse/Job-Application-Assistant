import json
from pathlib import Path
from config import JOBS_MATCHES_PATH


def save_matches(matches, file_to_save=JOBS_MATCHES_PATH):
    Path(file_to_save).write_text(json.dumps(matches, indent=2), encoding="utf-8")
