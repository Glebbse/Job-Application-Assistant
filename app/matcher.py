import logging

from app.models import JobListing, KeyWordAnalysisResult


logger = logging.getLogger(__name__)


def score_job(*, cv_text, job: JobListing, preferences: dict) -> KeyWordAnalysisResult:
    required_keywords = preferences["required_keywords"]
    preferred_keywords = preferences["preferred_keywords"]
    supporting_keywords = preferences["supporting_keywords"]
    min_preferred_words_matches = preferences["minimum_preferred_matches"]
    min_supporting_words_matches = preferences["minimum_supporting_matches"]
    tags_text = " ".join(job.tags).lower() if job.tags else ""
    description_text = job.description.lower()
    keyword_text = f"{description_text} {tags_text}".lower()

    matched_required_keywords = [
        kw for kw in required_keywords if kw in description_text
    ]
    matched_preferred_keywords = [
        kw for kw in preferred_keywords if kw in keyword_text
    ]
    matched_supporting_keywords = [
        kw for kw in supporting_keywords if kw in keyword_text
    ]
    matched_excluded_description_keywords = [
        kw
        for kw in preferences["excluded_description_keywords"]
        if kw in description_text
    ]

    keyword_score = (
        len(matched_required_keywords) * 25
        + len(matched_preferred_keywords) * 15
        + len(matched_supporting_keywords) * 10
    )
    passed_gate = True
    rejection_reason = None

    if not matched_required_keywords:
        passed_gate = False
        rejection_reason = "missing required keyword in description: " + ", ".join(
            required_keywords
        )
    elif matched_excluded_description_keywords:
        passed_gate = False
        rejection_reason = "excluded description keyword found: " + ", ".join(
            matched_excluded_description_keywords
        )
    elif len(matched_preferred_keywords) < min_preferred_words_matches:
        passed_gate = False
        rejection_reason = (
            "not enough preferred keywords matched: "
            f"{len(matched_preferred_keywords)} found, "
            f"{min_preferred_words_matches} required"
        )
    elif len(matched_supporting_keywords) < min_supporting_words_matches:
        passed_gate = False
        rejection_reason = (
            "not enough supporting keywords matched: "
            f"{len(matched_supporting_keywords)} found, "
            f"{min_supporting_words_matches} required"
        )

    return KeyWordAnalysisResult(
        keyword_score=keyword_score,
        matched_required_keywords=matched_required_keywords,
        matched_preferred_keywords=matched_preferred_keywords,
        matched_supporting_keywords=matched_supporting_keywords,
        passed_gate=passed_gate,
        rejection_reason=rejection_reason,
    )
