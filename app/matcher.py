KEYWORDS = [
    "python",
    "fastapi",
    "sql",
    "git",
    "rest api",
    "docker",
    "backend",
    "ai",
]

def score_job(cv_text, job):
    cv_lower = cv_text.lower()
    job_text = f"{job['title']} {job['description']} {job['company']}".lower()

    matched_keywords = [kw for kw in KEYWORDS if kw in cv_lower and kw in job_text]
    score = len(matched_keywords) * 10  # Simple scoring: 10 points per matched keyword

    return {
        "score": score,
        "matched_keywords": matched_keywords,
    }

