import json
from pathlib import Path
from app.config import JOBS_MATCHES_PATH
from app.models import SavedMatch


def save_json(data, file_to_save: str):
    path = Path(file_to_save)
    path.parent.mkdir(parents=True, exist_ok=True)
    Path(file_to_save).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def save_matches(matches, file_to_save=JOBS_MATCHES_PATH):
    save_json(matches, file_to_save=file_to_save)

def save_matches_by_country(*, matches: list[SavedMatch], country: str) -> None:
    path = Path(f"data/matches/by_country/{country}.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
    else:
        existing = []

    combined = existing + [match.model_dump() for match in matches]

    matches_by_url = {}
    for match in combined:
        url = match["job"]["url"]
        matches_by_url[url] = match

    deduped = list(matches_by_url.values())
    save_json(deduped, str(path))

