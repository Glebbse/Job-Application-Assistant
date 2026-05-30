import httpx

from app.storage import save_json

from app.config import ADZUNA_APP_ID, ADZUNA_APP_KEY

country = "ca"
page = 1

ADZUNA_URl = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"



all_raw_jobs = []
with httpx.Client(timeout=20) as client:
    response = client.get(ADZUNA_URl, params={
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY, 
                "what": "python developer", 
                "results_per_page": 20
                }, timeout=20)
    response.raise_for_status()
    data = response.json()
    all_raw_jobs.extend(data.get("results", []))
    jobs_by_id = {}
    for raw_job in all_raw_jobs:
        job_id = raw_job.get("id")
        if not job_id:
            continue
        jobs_by_id[job_id] = raw_job
    unique_raw_jobs = list(jobs_by_id.values()) 
adzuna_sample = save_json(unique_raw_jobs, "data/adzuna-samples.txt")

print(data)