# External RemoteOk API endpoint responds, but gives low-quality behaviour - fetching all the existing but limited by number jobs.
# A RemoteOK Ruby client says the /api feed is delayed by 24 hours, and that instant API access to all remote jobs is paid/high-budget. Source: remote-ok-ruby README.
# The API doesn't allow to apply query params to request, which leads to filtering all the fetched jobs by the client side.
# It is not guaranteed to contain:
# - every job visible on the website in real time
# - every historical job
# - only jobs matching your preferences
# - clean specific category/title only jobs
# This makes API difficult to rely on for accurate job fecthing and listings.
# Saved and kept for learning.

import httpx


from app.formatter import clean_html
from app.models import JobListing




def fetch_remoteok_jobs() -> list[JobListing]:
    with httpx.Client(timeout=20, headers={"User-Agent": "JobApplicationAssistant/0.1"}) as client:
        response = client.get("https://remoteok.com/api")
        response.raise_for_status()
        data = response.json()

    jobs = []
    for item in data:
        if isinstance(item, dict) and "id" in item:
            try:
                salary_min = item.get("salary_min")
                salary_max = item.get("salary_max")

                salary = None
                if salary_min or salary_max:
                    salary = f"{salary_min}-{salary_max}"
                item["description"] = clean_html(item.get("description", ""))
                job = JobListing(
                    title=item.get("position") or item.get("title") or "",
                    company=item.get("company") or "",
                    description=item.get("description") or "",
                    source="RemoteOK",
                    url=item.get("url") or "",
                    location=item.get("location") or "",
                    country=item.get("country", None),
                    job_type=item.get("job_type", "unknown"),
                    category=item.get("category", None),
                    tags=item.get("tags", []),
                    publication_date=item.get("date", None),
                    salary=salary,
                )

                jobs.append(job)
            except Exception as e:
                print(f"Error parsing job listing: {e}")
                continue

    return jobs
