
from app.models import JobListing, KeyWordAnalysisResult



def score_job(*, cv_text, job: JobListing, preferences: dict) -> KeyWordAnalysisResult:
    required_keywords = preferences["required_keywords"]
    preferred_keywords = preferences["preferred_keywords"]
    supporting_keywords = preferences["supporting_keywords"]
    positive_title_keywords = preferences["positive_title_keywords"]
    min_preferred_words_matches = preferences["minimum_preferred_matches"]
    min_supporting_words_matches = preferences["minimum_supporting_matches"]
    cv_lower = cv_text.lower()
    tags_text = " ".join(job.tags).lower() if job.tags else ""
    job_text = f"{job.title} {job.description} {tags_text} {job.category or ''}".lower()

    matched_required_keywords = [
        kw for kw in required_keywords if kw in job_text
    ]
    matched_positive_title_keywords = any(
        kw for kw in positive_title_keywords if kw in job.title.lower()
    )

    matched_excluded_description_keywords = [
        kw for kw in preferences["excluded_description_keywords"] if kw in job.description.lower()
    ]

    if matched_required_keywords == [] or not matched_positive_title_keywords or matched_excluded_description_keywords:
        passed_gate = False
        if not matched_required_keywords:
            reject = "missing required keyword: " + ", ".join(required_keywords)

        elif not matched_positive_title_keywords:
            reject = "title does not match target roles: " + ", ".join(positive_title_keywords)

        elif matched_excluded_description_keywords:
            reject = "excluded description keyword found: " + ", ".join(matched_excluded_description_keywords)

        return KeyWordAnalysisResult(
            keyword_score=0,
            matched_required_keywords=matched_required_keywords,
            matched_preferred_keywords=[],
            matched_supporting_keywords=[],
            matched_positive_title_keywords=matched_positive_title_keywords,
            passed_gate=passed_gate,
            rejection_reason=reject
        )

    else:
        title_match_score = 20
        matched_preferred_keywords = [
            kw for kw in preferred_keywords if kw in cv_lower and kw in job_text
        ]
        matched_supporting_keywords = [
            kw for kw in supporting_keywords if kw in cv_lower and kw in job_text
        ]

        passed_gate = (
            len(matched_preferred_keywords) >= min_preferred_words_matches
            and len(matched_supporting_keywords) >= min_supporting_words_matches
        )
        keyword_score = (
            len(matched_required_keywords) * 20
            + title_match_score
            + len(matched_preferred_keywords) * 15
            + len(matched_supporting_keywords) * 10
        )
        reject = None
        if len(matched_preferred_keywords) < min_preferred_words_matches:
            reject = f"not enough preferred keywords matched: {len(matched_preferred_keywords)} found, {min_preferred_words_matches} required"
        elif len(matched_supporting_keywords) < min_supporting_words_matches:
            reject = f"not enough supporting keywords matched: {len(matched_supporting_keywords)} found, {min_supporting_words_matches} required"
    return KeyWordAnalysisResult(
        keyword_score=keyword_score,
        matched_required_keywords=matched_required_keywords,
        matched_preferred_keywords=matched_preferred_keywords,
        matched_supporting_keywords=matched_supporting_keywords,
        matched_positive_title_keywords=matched_positive_title_keywords,
        passed_gate=passed_gate,
        rejection_reason=reject)
