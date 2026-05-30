#External Remotive API endpoint responds, but gives low-quality behaviour. 
# The API returns a lot of irrelevant jobs, and doesn't seem to properly filter by category or search term. 
# For example, searching for "python" returns many jobs that don't mention python at all. 
# This makes it difficult to rely on the API for accurate job listings.

import httpx

from app.formatter import clean_html
from app.models import JobListing


BASE_URL = "https://remotive.com/api/remote-jobs"

def fetch_remotive_jobs(*, queries: list[str]) -> list[JobListing]:
    all_raw_jobs = []
    with httpx.Client(timeout=20) as client:
        for query in queries:
            response = client.get(BASE_URL, params={"search": query}, timeout=20)
            response.raise_for_status()
            data = response.json()
            all_raw_jobs.extend(data.get("jobs", []))
    jobs_by_url = {}

    for raw_job in all_raw_jobs:
        raw_job["description"] = clean_html(raw_job.get("description", ""))
        jobs_by_url[raw_job["url"]] = raw_job
    unique_raw_jobs = list(jobs_by_url.values())


    jobs = [
        JobListing(
            title=job["title"],
            company=job["company_name"],
            description=job["description"],
            source="remotive",
            url=job["url"],
            location=job.get("candidate_required_location"),
            country=None,
            job_type="remote",
            category=job.get("category"),
            tags=job.get("tags", []),
            publication_date=job.get("publication_date"),
            salary=job.get("salary"),
        )
        for job in unique_raw_jobs
    ]

    return jobs