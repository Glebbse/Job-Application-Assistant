import json
from pathlib import Path
from app.config import JOBS_MATCHES_PATH


def save_json(data, file_to_save: str):
    Path(file_to_save).write_text(json.dumps(data, indent=2), encoding="utf-8")

def save_matches(matches, file_to_save=JOBS_MATCHES_PATH):
    save_json(matches, file_to_save=file_to_save)


