



from app.models import JobListing


def filter_jobs_by_profile(
        *, 
        jobs: list[JobListing], 
        prefs: dict) -> list[JobListing]:
    filtered_jobs = []
    positive_title_keywords = prefs["positive_title_keywords"]
    source_excluded_title_keywords = prefs["source_excluded_title_keywords"]
    allowed_categories = prefs["allowed_categories"]
    
    for job in jobs:

        has_excluded_title = any(kw.lower() in job.title for kw in source_excluded_title_keywords)
        has_positive_title = any(kw.lower() in job.title for kw in positive_title_keywords)

        
        if has_excluded_title:
            continue

        if not has_positive_title:
            continue
        
        category = (job.category or "").lower()
        if category and allowed_categories:
            allowed_category = any(
                allowed_category.lower() == category for allowed_category in allowed_categories
            )
            if not allowed_category:
                continue

        filtered_jobs.append(job)

    return filtered_jobs

        
