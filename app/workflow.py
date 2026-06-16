from datetime import datetime
from pathlib import Path

import json
import logging

from openai import RateLimitError


from app.importers.adzuna import fetch_adzuna_jobs
from app.job_filtering import filter_jobs_by_profile
from app.ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai, is_retryable_rate_limit
from app.config import (ADZUNA_COUNTRIES, ADZUNA_COUNTRY, CV_PATH, PROFILE_PATH, 
                        DAILY_APPLY_TARGET, USE_MOCK_AI
)
from app.exceptions import format_ai_error
from app.importers.manual_json import load_jobs_from_json
from app.importers.remoteok import fetch_remoteok_jobs
from app.importers.remotive import fetch_remotive_jobs
from app.matcher import score_job
from app.models import FetchedJobsBatches, RunMetaData, RunResult, RunSummary, SavedMatch
from app.storage import save_matches_by_country, save_json, save_matches


logger= logging.getLogger(__name__)

def fetch_jobs(*, source: str, country: str | None = None) -> list[FetchedJobsBatches]:
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)
    queries = prefs["target_roles"]
    batches = []
    def resolve_countries(*, source: str, country: str | None) -> list[str | None]:
        if source != "adzuna":
            return [None]
        if country == "multi" and source == "adzuna":
            return ADZUNA_COUNTRIES
        
        return [country or ADZUNA_COUNTRY]

    def build_jobs_path(*, source: str, country: str | None) -> str:
        if country: 
            return f"data/fetched_jobs/{source}/{country}.json"
        return f"data/fetched_jobs/{source}/latest.json"

    countries = resolve_countries(source=source, country=country)
    for current_country in countries:
        if source == "remotive":
            fetched_jobs = fetch_remotive_jobs(queries=queries)
        elif source == "remoteok":
            fetched_jobs = fetch_remoteok_jobs()
        elif source == "adzuna":
            fetched_jobs = fetch_adzuna_jobs(country=current_country, queries=queries)
        else:
            raise ValueError(f"unknown source {source}")
        output_path = build_jobs_path(source=source, country=current_country)

        filtered_jobs = filter_jobs_by_profile(jobs=fetched_jobs, prefs=prefs)
        
        batches.append(FetchedJobsBatches(
            source=source,
            country=current_country,
            fetched_jobs=fetched_jobs,
            filtered_jobs=filtered_jobs,
            jobs_path=output_path
        ))

        save_json([job.model_dump() for job in filtered_jobs], output_path)
    return batches

def analyze_jobs(*, source: str, jobs_path: str) -> list[SavedMatch]:
    cv = Path(CV_PATH).read_text(encoding="utf-8")
    prefs_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    prefs = json.loads(prefs_text)
    jobs = load_jobs_from_json(jobs_path)
    if not jobs:
        logger.info("No jobs found in %s", jobs_path)
        return []
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
            except RateLimitError:
                raise
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

    return matches



def run_full_pipeline(*, source: str, country: str | None) -> RunResult:
    batches = fetch_jobs(source=source, country=country)
    total_fetched = 0
    total_filtered = 0
    total_ai_analyzed = 0
    total_apply = 0
    total_maybe = 0
    total_skip = 0
    total_errors = 0
    countries = []
    for batch in batches:
        try:
            matches = analyze_jobs(source=source, jobs_path=batch.jobs_path)
            fetched_count = len(batch.fetched_jobs)
            filtered_count = len(batch.filtered_jobs)
        except RateLimitError as e:
            if not is_retryable_rate_limit(e):
                logger.warning("Daily rate limit reached. Stopping pipeline. Error: %s", str(e))
                break
            raise
        if len(matches) != 0: 
            save_matches_by_country(matches=matches, country=batch.country or "unknown")
            logger.info("Total matches saved: %s. Analysis is done.", len(matches))
        total_fetched += fetched_count
        total_filtered += filtered_count
        total_ai_analyzed += len(matches)
        total_apply += sum(1 for match in matches if match.ai_analysis and match.ai_analysis.recommendation == "apply")
        total_maybe += sum(1 for match in matches  if match.ai_analysis and match.ai_analysis.recommendation == "maybe")
        total_skip += sum(1 for match in matches  if match.ai_analysis and match.ai_analysis.recommendation == "skip")
        total_errors += sum(1 for match in matches if match.ai_error)
        countries.append(batch.country or "unknown")
    summary = RunSummary(
        fetched_jobs=total_fetched,
        filtered_jobs=total_filtered,
        ai_analyzed=total_ai_analyzed, 
        apply_count=total_apply, 
        maybe_count=total_maybe, 
        skip_count=total_skip, 
        error_count=total_errors
    )
    started_at = datetime.now().isoformat(timespec="seconds")
    file_stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    metadata = RunMetaData(
        started_at=started_at, 
        source=source, 
        country=country, 
        target_apply_count=DAILY_APPLY_TARGET
    )
    run_result = RunResult(
        run=metadata, 
        summary=summary, 
        countries=countries
    )
    save_json(run_result.model_dump(), f"data/runs/{file_stamp}_{source}.json")
        
    return run_result
