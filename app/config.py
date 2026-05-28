import os
from dotenv import load_dotenv


load_dotenv()

MIN_SCORE = int(os.getenv("MIN_SCORE", "40"))
CV_PATH = os.getenv("CV_PATH", "data/cv.md")
JOBS_PATH = os.getenv("JOBS_PATH", "data/sample_jobs.json")
JOBS_MATCHES_PATH = os.getenv("JOBS_MATCHES_PATH", "data/matches.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROFILE_PATH = os.getenv("PROFILE_PATH", "data/profile.json")
USE_MOCK_AI = os.getenv("USE_MOCK_AI", "true").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
REMOTIVE_JOBS_PATH = os.getenv("REMOTIVE_JOBS_PATH", "data/remotive_jobs.json")
JOB_SEARCH_QUERIES = os.getenv("JOB_SEARCH_QUERIES", "python,fastapi,backend,postgresql").split(",")
REMOTEOK_JOBS_PATH = os.getenv("REMOTEOK_JOBS_PATH", "data/remoteok_jobs.json")
REMOTEOK_JOBS_WITHOUT_FILTERS = os.getenv("REMOTEOK_JOBS_WITHOUT_FILTERS", "data/remoteok_jobs_samples.json")