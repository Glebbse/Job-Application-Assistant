from pathlib import Path

import pytest

from app.importers.remotive import fetch_remotive_jobs
from app.models import JobListing
from app.storage import save_json


@pytest.mark.integration
def test_fetch_remotive_jobs_returns_jobs_live_api():
    queries = ["python", "fastapi", "backend"]
    jobs = fetch_remotive_jobs(queries=queries)
    assert isinstance(jobs, list)
    assert len(jobs) > 0
    for job in jobs:
        assert isinstance(job, JobListing)
        assert job.title
        assert job.company
        assert job.description
        assert job.url

    save_json([job.model_dump() for job in jobs], file_to_save="tests/test_remotive_jobs.json")
    assert Path("data/test_remotive_jobs.json").exists()