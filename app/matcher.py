from app.models import JobListing, KeyWordAnalysisResult



def score_job(*, cv_text, job: JobListing, preferences: dict) -> KeyWordAnalysisResult:
    core_keywords = preferences["core_keywords"]
    supporting_keywords = preferences["supporting_keywords"]
    min_core_matches = preferences["minimum_core_matches"]
    min_supporting_matches = preferences["minimum_supporting_matches"]
    cv_lower = cv_text.lower()
    job_text = f"{job.title} {job.description} {job.company}".lower()

    matched_core_keywords = [
        kw for kw in core_keywords if kw in cv_lower and kw in job_text
    ]
    matched_supporting_keywords = [
        kw for kw in supporting_keywords if kw in cv_lower and kw in job_text
    ]
    passed_gate = (
        len(matched_core_keywords) >= min_core_matches
        and len(matched_supporting_keywords) >= min_supporting_matches
    )
    keyword_score = (
        len(matched_core_keywords) * 20
        + len(matched_supporting_keywords) * 10
    )

    return KeyWordAnalysisResult(
        keyword_score=keyword_score,
        matched_core_keywords=matched_core_keywords,
        matched_supporting_keywords=matched_supporting_keywords,
        passed_gate=passed_gate,)
