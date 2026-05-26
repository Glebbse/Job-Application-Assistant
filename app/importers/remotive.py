import httpx

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
            job_type="remote"
        )
        for job in unique_raw_jobs
    ]

    return jobs