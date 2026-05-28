


from pathlib import Path

import json

from app.job_filtering import filter_jobs_by_profile
from app.ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai
from app.config import CV_PATH, JOB_SEARCH_QUERIES, PROFILE_PATH, REMOTEOK_JOBS_PATH, REMOTIVE_JOBS_PATH, USE_MOCK_AI, REMOTEOK_JOBS_WITHOUT_FILTERS
from app.exceptions import format_ai_error
from app.importers.manual_json import load_jobs_from_json
from app.importers.remoteok import fetch_remoteok_jobs
from app.importers.remotive import fetch_remotive_jobs
from app.matcher import score_job
from app.models import JobListing, SavedMatch
from app.storage import save_json, save_matches


def fetch_jobs(*, source: str) -> list[JobListing]:
    remoteok_jobs_samples = REMOTEOK_JOBS_WITHOUT_FILTERS
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)
    if source == "remotive":
        jobs = fetch_remotive_jobs(queries=JOB_SEARCH_QUERIES)
        output_path = REMOTIVE_JOBS_PATH
    elif source == "remoteok":
        jobs = fetch_remoteok_jobs()
        output_path = REMOTEOK_JOBS_PATH
    else:
        raise ValueError(f"unknown source {source}")
    remoteok_wothout_filters = save_json([job.model_dump() for job in jobs], remoteok_jobs_samples)
    print("samples without filters saved")
    jobs = filter_jobs_by_profile(jobs=jobs, prefs=prefs)
    save_json([job.model_dump() for job in jobs], output_path)
    return jobs

def analyze_jobs(*, source: str) -> list[SavedMatch]:
    cv = Path(CV_PATH).read_text(encoding="utf-8")
    if source == "remotive":
        jobs = load_jobs_from_json(REMOTIVE_JOBS_PATH)
    elif source == "remoteok":
        jobs = load_jobs_from_json(REMOTEOK_JOBS_PATH)
    else:
        raise ValueError("unknown source {source}")
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)

    matches = []
    for job in jobs:
        keyword_analysis = score_job(cv_text=cv, job=job, preferences=prefs)
        if keyword_analysis.passed_gate:
            ai_analysis = None
            ai_error = None
            try:
                if USE_MOCK_AI:
                    ai_analysis = analyze_job_with_mock_ai(cv_text=cv, job=job, preferences=prefs)
                else:
                    ai_analysis = analyze_job_with_ai(cv_text=cv, job=job, preferences=prefs)
            except Exception as e:
                ai_error = format_ai_error(e)
            match = SavedMatch(
                job=job,
                keyword_analysis=keyword_analysis,
                ai_analysis=ai_analysis,
                ai_error=ai_error
            )
            matches.append(match)
    save_matches([match.model_dump() for match in matches])
    return matches

def run_full_pipeline(*, source: str):
    fetch_jobs(source=source)
    return analyze_jobs(source=source)