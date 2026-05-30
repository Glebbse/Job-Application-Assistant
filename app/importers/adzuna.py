import httpx
import logging


from app.formatter import clean_html
from app.models import JobListing
from app.config import ADZUNA_APP_ID, ADZUNA_APP_KEY


logger = logging.getLogger(__name__)


def fetch_adzuna_jobs(*, country: str = "ca", queries: list[str], page: int = 1, results_per_page: int = 20) -> list[JobListing]:
    logger.info("Fetching jobs from Adzuna: country - %s queries - %s", country, queries)
    adzuna_url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    all_raw_jobs = []
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise ValueError("ADZUNA_APP_ID and ADZUNA_APP_KEY must be set")
    try: 
        with httpx.Client(timeout=20) as client:
            for query in queries:
                logger.info("Sending request with query %s", query)

                response = client.get(adzuna_url, params={
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_APP_KEY, 
                    "what": query, 
                    "results_per_page": results_per_page
                    }, timeout=20)
                response.raise_for_status()
                data = response.json()
                all_raw_jobs.extend(data.get("results", []))
            
            logger.info(f"Fetched raw jobs: {len(all_raw_jobs)}")

            jobs_by_id = {}
            for raw_job in all_raw_jobs:
                salary_min = raw_job.get("salary_min")
                salary_max = raw_job.get("salary_max")
                salary = None
                if salary_min or salary_max:
                    salary = f"{salary_min}-{salary_max}"
                location_parts = raw_job.get("location", {}).get("area", [])
                clean_location_parts = [
                    clean_html(str(part))
                    for part in location_parts
                    if part
                    ]
                location = ", ".join(clean_location_parts)
                raw_job["location"] = location
                raw_job["salary_is_predicted"] = salary
                job_id = raw_job.get("id")
                if not job_id:
                    logger.warning("Skipping job without id: %s", raw_job.get("title"))
                    continue
                jobs_by_id[job_id] = raw_job
        unique_raw_jobs = list(jobs_by_id.values())
        logger.info("Deduplicated %s jobs", len(unique_raw_jobs))
    except httpx.HTTPStatusError as error:
        logger.error("Adzuna HTTPStatusError: %s", error)
        raise RuntimeError(f"Adzuna API returned HTTP error: {error.response.status_code}") from error

    except httpx.RequestError as error:
        logger.error("Adzuna API request failed: %s", error)
        raise RuntimeError(f"Could not connect to Adzuna API: {error}") from error

    jobs = [
        JobListing(
            title=job["title"], 
            company=job["company"].get("display_name"),
            description=clean_html(job.get("description", "")), 
            source="adzuna", 
            url=job.get("redirect_url", ""), 
            location=job["location"], 
            country=country, 
            job_type="unknown", 
            category=job["category"].get("label", "None"), 
            tags=[job["category"].get("tag")] if job["category"].get("tag") else [], 
            publication_date=job["created"], 
            salary=job["salary_is_predicted"]
        )
        for job in unique_raw_jobs        
    ]
    logger.info("Jobs serializing done, number of jobs: %s", len(jobs))

    return jobs