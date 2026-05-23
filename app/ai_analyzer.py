from openai import OpenAI
import json

from config import OPENAI_API_KEY, OPENAI_MODEL
from models import AIAnalysis, JobListing


model=OPENAI_MODEL


def analyze_job_with_ai(*, cv_text: str, job: JobListing, preferences: dict) -> AIAnalysis:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set. Skipping AI analysis.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
    You are analyzing whether a job is worth applying to for this candidate.

    Use the candidate CV, candidate preferences, and job listing.
    Return a realistic assessment.

    Scoring:
    - fit_score: 0-100, how well the job matches the candidate's skills, goals, stack, and preferences.
    - interview_chance_score: 0-100, how realistic it is that applying could lead to an interview.

    Recommendation:
    - apply: strong fit and realistic enough chance
    - maybe: some fit, but meaningful risks
    - skip: weak fit, wrong direction, too senior, wrong location, or low chance

    Rules:
    - Do not invent company information.
    - If company details are not present in the listing, set company_description to "Not provided in listing".
    - Be honest and practical.
    - Prefer concise, useful explanations.

    Candidate CV:
    {cv_text}

    Candidate preferences:
    {json.dumps(preferences, indent=2)}

    Job listing:
    {json.dumps(job.model_dump(), indent=2)}
    """
    
    response = client.responses.parse(
        model=OPENAI_MODEL, 
        input=prompt, 
        text_format=AIAnalysis, 
        )

    return response.output_parsed


def analyze_job_with_mock_ai(*, cv_text: str, job: dict, preferences: dict) -> AIAnalysis:
    # This is a mock function to simulate AI analysis for testing purposes.
    return AIAnalysis(
        fit_score=75,
        interview_chance_score=60,
        recommendation="maybe",
        summary="The candidate has relevant experience but may lack some specific skills mentioned in the job listing.",
        strengths=["Relevant experience", "Good communication skills"],
        gaps=["Lack of specific technical skill", "Limited experience in the industry"],
        role_description=job.get("description", "Not provided in listing"),
        company_description=job.get("company", "Not provided in listing"),
        application_advice="Consider applying if you can address the skill gap in your cover letter."
    )