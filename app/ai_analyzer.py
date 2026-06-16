from pathlib import Path

from openai import OpenAI, RateLimitError
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception
import json

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.models import AIAnalysis, JobListing


model=OPENAI_MODEL


def is_retryable_rate_limit(error: BaseException) -> bool:
    if not isinstance(error, RateLimitError):
        return False
    error_text = str(error).lower()

    if "requests per day" in error_text or "rpd" in error_text or "daily limit" in error_text:
        return False
    return True

@retry(
        wait=wait_random_exponential(min=6, max=60), 
        stop=stop_after_attempt(5),
        retry=retry_if_exception(is_retryable_rate_limit),
        reraise=True
)
def call_openai_with_backoff(*, client: OpenAI, prompt: str) -> AIAnalysis:
    response = client.responses.parse(
        model=OPENAI_MODEL, 
        input=prompt, 
        text_format=AIAnalysis
    )
    return response.output_parsed

def analyze_job_with_ai(*, cv_text: str, job: JobListing, preferences: dict) -> AIAnalysis:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Skipping AI analysis.")
    
    client = OpenAI(api_key=OPENAI_API_KEY, max_retries=0)
    prompt_template = Path("prompts/job_analysis.txt").read_text(encoding="utf-8")

    prompt = prompt_template.format(
        cv_text=cv_text,
        preferences_json=json.dumps(preferences, indent=2),
        job_json=json.dumps(job.model_dump(), indent=2),
    )
   
    return call_openai_with_backoff(client=client, prompt=prompt)


def analyze_job_with_mock_ai(*, cv_text: str, job: JobListing, preferences: dict) -> AIAnalysis:
    # This is a mock function to simulate AI analysis for testing purposes.
    return AIAnalysis(
        fit_score=75,
        interview_chance_score=60,
        recommendation="maybe",
        summary="The candidate has relevant experience but may lack some specific skills mentioned in the job listing.",
        strengths=["Relevant experience", "Good communication skills"],
        gaps=["Lack of specific technical skill", "Limited experience in the industry"],
        role_description=job.description or "Not provided in listing",
        company_description=job.company or "Not provided in listing",
        application_advice="Consider applying if you can address the skill gap in your cover letter."
    )