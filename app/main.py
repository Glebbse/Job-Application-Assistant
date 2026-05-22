import json
from pathlib import Path

from storage import save_matches
from matcher import score_job
from config import MIN_SCORE, CV_PATH, JOBS_PATH, JOBS_MATCHES_PATH, PROFILE_PATH


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
        result = score_job(cv, job, preferences)
        print(f"Job Title: {job['title']} at {job['company']}")
        print(f"Score: {result['keyword_score']}")
        print(f"Matched Keywords: {', '.join(result['matched_core_keywords'] + result['matched_supporting_keywords'])}")
        print()

        if result["passed_gate"]:
            matches.append({
                "job": job,
                "analysis": result, 
                })
            
    save_matches(matches)
    print(f"Total matches found: {len(matches)}. Results saved to {JOBS_MATCHES_PATH}")


if __name__ == "__main__":
    main()