import json
from pathlib import Path

def save_matches(matches, filename="matches.json"):
    Path(filename).write_text(json.dumps(matches, indent=2), encoding="utf-8")
