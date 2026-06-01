from datetime import datetime
from pathlib import Path

import json
import logging

from app.importers.adzuna import fetch_adzuna_jobs
from app.job_filtering import filter_jobs_by_profile
from app.ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai
from app.config import (CV_PATH, PROFILE_PATH, REMOTEOK_JOBS_PATH, 
                        REMOTIVE_JOBS_PATH, USE_MOCK_AI, ADZUNA_JOBS_PATH, ADZUNA_COUNTRY, 
                        DAILY_APPLY_TARGET
)
from app.exceptions import format_ai_error
from app.importers.manual_json import load_jobs_from_json
from app.importers.remoteok import fetch_remoteok_jobs
from app.importers.remotive import fetch_remotive_jobs
from app.matcher import score_job
from app.models import JobListing, RunMetaData, RunResult, RunSummary, SavedMatch
from app.storage import save_matches_by_country, save_json, save_matches


logger= logging.getLogger(__name__)

def fetch_jobs(*, source: str) -> tuple[list[JobListing], list[JobListing]]:
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)
    queries = prefs["target_roles"]
    if source == "remotive":
        fetched_jobs = fetch_remotive_jobs(queries=queries)
        output_path = REMOTIVE_JOBS_PATH
    elif source == "remoteok":
        fetched_jobs = fetch_remoteok_jobs()
        output_path = REMOTEOK_JOBS_PATH
    elif source == "adzuna":
        country = ADZUNA_COUNTRY
        fetched_jobs = fetch_adzuna_jobs(country=country, queries=queries)
        output_path = ADZUNA_JOBS_PATH
    else:
        raise ValueError(f"unknown source {source}")
    filtered_jobs = filter_jobs_by_profile(jobs=fetched_jobs, prefs=prefs)
    save_json([job.model_dump() for job in filtered_jobs], output_path)
    return fetched_jobs, filtered_jobs

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
    fetched_jobs, filtered_jobs = fetch_jobs(source=source)
    matches = analyze_jobs(source=source)
    apply_count = sum(1 for match in matches if match.ai_analysis and match.ai_analysis.recommendation == "apply")
    maybe_count = sum(1 for match in matches  if match.ai_analysis and match.ai_analysis.recommendation == "maybe")
    skip_count = sum(1 for match in matches  if match.ai_analysis and match.ai_analysis.recommendation == "skip")
    error_count = sum(1 for match in matches if match.ai_error)

    summary = RunSummary(
        fetched_jobs=len(fetched_jobs),
        filtered_jobs=len(filtered_jobs),
        ai_analyzed=len(matches), 
        apply_count=apply_count, 
        maybe_count=maybe_count, 
        skip_count=skip_count, 
        error_count=error_count
    )
    started_at = datetime.now().isoformat(timespec="seconds")
    file_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    metadata = RunMetaData(
        started_at=started_at, 
        source=source, 
        country=ADZUNA_COUNTRY if source == "adzuna" else None, 
        target_apply_count=DAILY_APPLY_TARGET
    )
    run_result = RunResult(
        run=metadata, 
        summary=summary, 
        matches=matches
    )
    save_json(run_result.model_dump(), f"data/runs/{file_stamp}_{source}.json")
    
    save_matches_by_country(matches=matches, country=metadata.country or "unknown")
    
    return run_result
