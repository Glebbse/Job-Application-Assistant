import json
from pathlib import Path

from storage import save_matches
from matcher import score_job
from config import CV_PATH, JOBS_PATH, JOBS_MATCHES_PATH, PROFILE_PATH, USE_MOCK_AI
from ai_analyzer import analyze_job_with_ai, analyze_job_with_mock_ai
from formatter import format_match_result

matches = []

def main():
    cv = Path(CV_PATH).read_text(encoding="utf-8")
    jobs_text = Path(JOBS_PATH).read_text(encoding="utf-8")
    jobs = json.loads(jobs_text)
    pref_text = Path(PROFILE_PATH).read_text(encoding="utf-8")
    preferences = json.loads(pref_text)

    print(f"CV loaded: {len(cv)} characters")
    print(f"Jobs loaded: {len(jobs)} entries")

    for job in jobs:
        keyword_analysis = score_job(cv_text=cv, job=job, preferences=preferences)
        if keyword_analysis["passed_gate"]:
            if USE_MOCK_AI:
                ai_analysis = analyze_job_with_mock_ai(cv_text=cv, job=job, preferences=preferences)
            else:
                ai_analysis = analyze_job_with_ai(cv_text=cv, job=job, preferences=preferences)

            matches.append({
                "job": job,
                "keyword_analysis": keyword_analysis,
                "ai_analysis": ai_analysis.model_dump(),
                })
            print(format_match_result(job=job, keyword_analysis=keyword_analysis, ai_analysis=ai_analysis))


    save_matches(matches)
    print(f"Total matches found: {len(matches)}. Results saved to {JOBS_MATCHES_PATH}")


if __name__ == "__main__":
    main()