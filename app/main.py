import json
from pathlib import Path

from importers.manual_json import load_jobs_from_json
from storage import save_matches
from matcher import score_job
from config import CV_PATH, JOBS_PATH, JOBS_MATCHES_PATH, PROFILE_PATH, USE_MOCK_AI
from ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai
from formatter import format_match_result
from exceptions import format_ai_error


def main():
    matches = []
    cv = Path(CV_PATH).read_text(encoding="utf-8")
    jobs = load_jobs_from_json(JOBS_PATH)

    pref_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    preferences = json.loads(pref_text)

    print(f"CV loaded: {len(cv)} characters")
    print(f"Jobs loaded: {len(jobs)} entries")

    for job in jobs:
        keyword_analysis = score_job(cv_text=cv, job=job, preferences=preferences)
        if keyword_analysis["passed_gate"]:
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

            matches.append({
                "job": job.model_dump(),
                "keyword_analysis": keyword_analysis,
                "ai_analysis": ai_analysis.model_dump() if ai_analysis else None,
                "ai_error": ai_error
                })
            print(format_match_result(job=job, keyword_analysis=keyword_analysis, ai_analysis=ai_analysis))


    save_matches(matches)
    print(f"Total matches found: {len(matches)}. Results saved to {JOBS_MATCHES_PATH}")


if __name__ == "__main__":
    main()