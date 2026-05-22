import os
from dotenv import load_dotenv


load_dotenv()

MIN_SCORE = int(os.getenv("MIN_SCORE", "40"))
CV_PATH = os.getenv("CV_PATH", "data/cv.md")
JOBS_PATH = os.getenv("JOBS_PATH", "data/sample_jobs.json")
JOBS_MATCHES_PATH = os.getenv("MATCHES_PATH", "data/matches.json")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")