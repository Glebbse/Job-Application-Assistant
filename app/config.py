import os
from dotenv import load_dotenv


load_dotenv()

MIN_SCORE = int(os.getenv("MIN_SCORE", "40"))
CV_PATH = os.getenv("CV_PATH", "data/cv.md")
JOBS_PATH = os.getenv("JOBS_PATH", "data/sample_jobs.json")
LAST_JOBS_MATCHES_PATH = os.getenv("LAST_JOBS_MATCHES_PATH", "data/matches/last_matches.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROFILE_PATH = os.getenv("PROFILE_PATH", "data/profile.json")
USE_MOCK_AI = os.getenv("USE_MOCK_AI", "true").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
REMOTIVE_JOBS_PATH = os.getenv("REMOTIVE_JOBS_PATH", "data/fetched_jobs/remotive_jobs.json")
REMOTEOK_JOBS_PATH = os.getenv("REMOTEOK_JOBS_PATH", "data/fetched_jobs/remoteok_jobs.json")
REMOTEOK_JOBS_WITHOUT_FILTERS = os.getenv("REMOTEOK_JOBS_WITHOUT_FILTERS", "data/fetched_jobs/remoteok_jobs_samples.json")
ADZUNA_JOBS_PATH = os.getenv("ADZUNA_JOBS_PATH", f"data/fetched_jobs/adzuna_jobs.json")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_COUNTRY=os.getenv("ADZUNA_COUNTRY", "ca")
ADZUNA_COUNTRIES = [
    country.strip()
    for country in os.getenv("ADZUNA_COUNTRIES", "ca").split(",")
    if country.strip()
]
DAILY_APPLY_TARGET= int(os.getenv("DAILY_APPLY_TARGET", "10"))
