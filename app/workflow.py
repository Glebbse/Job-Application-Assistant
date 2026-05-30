from pathlib import Path

import json
import logging

from app.importers.adzuna import fetch_adzuna_jobs
from app.job_filtering import filter_jobs_by_profile
from app.ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai
from app.config import (CV_PATH, PROFILE_PATH, REMOTEOK_JOBS_PATH, 
                        REMOTIVE_JOBS_PATH, USE_MOCK_AI, ADZUNA_JOBS_PATH)
from app.exceptions import format_ai_error
from app.importers.manual_json import load_jobs_from_json
from app.importers.remoteok import fetch_remoteok_jobs
from app.importers.remotive import fetch_remotive_jobs
from app.matcher import score_job
from app.models import JobListing, SavedMatch
from app.storage import save_json, save_matches


logger= logging.getLogger(__name__)

def fetch_jobs(*, source: str) -> list[JobListing]:
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)
    queries = prefs["target_roles"]
    if source == "remotive":
        jobs = fetch_remotive_jobs(queries=queries)
        output_path = REMOTIVE_JOBS_PATH
    elif source == "remoteok":
        jobs = fetch_remoteok_jobs()
        output_path = REMOTEOK_JOBS_PATH
    elif source == "adzuna":
        jobs = fetch_adzuna_jobs(queries=queries)
        output_path = ADZUNA_JOBS_PATH
    else:
        raise ValueError(f"unknown source {source}")
    jobs = filter_jobs_by_profile(jobs=jobs, prefs=prefs)
    save_json([job.model_dump() for job in jobs], output_path)
    return jobs

def analyze_jobs(*, source: str) -> list[SavedMatch]:
    cv = Path(CV_PATH).read_text(encoding="utf-8")
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)
    if source == "remotive":
        jobs = load_jobs_from_json(REMOTIVE_JOBS_PATH)
    elif source == "remoteok":
        jobs = load_jobs_from_json(REMOTEOK_JOBS_PATH)
    elif source == "adzuna":
        jobs = load_jobs_from_json(ADZUNA_JOBS_PATH)
    else:
        raise ValueError("unknown source {source}")
    matches = []
    for job in jobs:
        logger.info("Keyword Analysis begins for %s ...", job.title)
        keyword_analysis = score_job(cv_text=cv, job=job, preferences=prefs)
        if keyword_analysis.passed_gate:
            logger.info("Keyword gate passed %s with score %s", 
                        job.title, 
                        keyword_analysis.keyword_score)
            ai_analysis = None
            ai_error = None
            try:
                if USE_MOCK_AI:
                    ai_analysis = analyze_job_with_mock_ai(cv_text=cv, job=job, preferences=prefs)
                else:
                    ai_analysis = analyze_job_with_ai(cv_text=cv, job=job, preferences=prefs)
            except Exception as e:
                logger.error("Error occured: %s", str(e))
                ai_error = format_ai_error(e)
            match = SavedMatch(
                job=job,
                keyword_analysis=keyword_analysis,
                ai_analysis=ai_analysis,
                ai_error=ai_error
            )
            matches.append(match)
            logger.info("AI analysis is done for %s, result appended to matches. Processing next...", job.title)
        else:
            logger.info("Keyword gate rejected %s. Rejection reason: %s", job.title, keyword_analysis.rejection_reason)
    if len(matches) != 0: 
        save_matches([match.model_dump() for match in matches])
        logger.info("Total matches saved: %s. Analysis is done.", len(matches))

    return matches

def run_full_pipeline(*, source: str):
    fetch_jobs(source=source)
    return analyze_jobs(source=source)