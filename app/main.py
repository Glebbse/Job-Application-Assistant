import json
from pathlib import Path

from app.importers.remotive import fetch_remotive_jobs
from app.models import SavedMatch
from app.importers.manual_json import load_jobs_from_json
from app.storage import save_json, save_matches
from app.matcher import score_job
from app.config import CV_PATH, JOB_SEARCH_QUERIES, JOBS_MATCHES_PATH, PROFILE_PATH, REMOTIVE_JOBS_PATH, USE_MOCK_AI
from app.ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai
from app.formatter import format_match_result
from app.exceptions import format_ai_error


def main():
    matches = []
    cv = Path(CV_PATH).read_text(encoding="utf-8")
    remotive_jobs = fetch_remotive_jobs(queries=JOB_SEARCH_QUERIES)
    save_json([job.model_dump() for job in remotive_jobs], file_to_save=REMOTIVE_JOBS_PATH)
    jobs = load_jobs_from_json(REMOTIVE_JOBS_PATH)

    pref_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    preferences = json.loads(pref_text)

    print(f"CV loaded: {len(cv)} characters")
    print(f"Jobs loaded: {len(jobs)} entries")

    for job in jobs:
        keyword_analysis = score_job(cv_text=cv, job=job, preferences=preferences)
        if keyword_analysis.passed_gate:
            ai_analysis = None
            ai_error = None
            try:
                if USE_MOCK_AI:
                    ai_analysis = analyze_job_with_mock_ai(cv_text=cv, job=job, preferences=preferences)
                else:
                    ai_analysis = analyze_job_with_ai(cv_text=cv, job=job, preferences=preferences)
            except Exception as e:
                    ai_error = format_ai_error(e)
                    print(ai_error)

            match = SavedMatch(
                job=job,
                keyword_analysis=keyword_analysis,
                ai_analysis=ai_analysis,
                ai_error=ai_error
            )
            matches.append(match)
            print(format_match_result(job=job, keyword_analysis=keyword_analysis, ai_analysis=ai_analysis))


    save_matches([match.model_dump() for match in matches], file_to_save=JOBS_MATCHES_PATH)
    print(f"Total matches found: {len(matches)}. Results saved to {JOBS_MATCHES_PATH}")


if __name__ == "__main__":
    main()