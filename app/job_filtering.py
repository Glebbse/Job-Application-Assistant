import logging



from app.models import JobListing


logger = logging.getLogger(__name__)

def filter_jobs_by_profile(
        *, 
        jobs: list[JobListing], 
        prefs: dict) -> list[JobListing]:
    filtered_jobs = []
    positive_title_keywords = prefs["positive_title_keywords"]
    source_excluded_title_keywords = prefs["source_excluded_title_keywords"]
    allowed_categories = [c.lower() for c in prefs["allowed_categories"]]
    logger.info("Filtering jobs begins, number of jobs: %s", len(jobs))

    for job in jobs:
        has_python_signal = "python" in job.title.lower()
        has_excluded_title = any(kw.lower() in job.title.lower() for kw in source_excluded_title_keywords)
        has_positive_title = any(kw.lower() in job.title.lower() for kw in positive_title_keywords)

        category = (job.category or "").lower()
        if category and category not in allowed_categories:
            logger.warning("Job contains unallowed category: %s, skipping job", job.category)
            continue
        
        if has_excluded_title and not has_positive_title and not has_python_signal:
            logger.warning("Job has excluded title: %s, skipping job", job.title)
            continue

        if not has_positive_title:
            logger.warning("Job does not have positive title. Title: %s, skipping job", job.title)
            continue

        filtered_jobs.append(job)

    logger.info("Filtering jobs done, number of jobs: %s", len(filtered_jobs))

    return filtered_jobs

        
