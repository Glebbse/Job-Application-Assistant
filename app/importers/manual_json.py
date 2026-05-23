from pathlib import Path

import json

from models import JobListing


def load_jobs_from_json(file_path: str) -> list[JobListing]:
    jobs_text = Path(file_path).read_text(encoding="utf-8")
    jobs_raw = json.loads(jobs_text)
    return [JobListing(**job) for job in jobs_raw]