from typing import Literal

from pydantic import BaseModel, Field

class AIAnalysis(BaseModel):
    fit_score: int = Field(ge=0, le=100)
    interview_chance_score: int = Field(ge=0, le=100)
    recommendation: Literal["apply", "maybe", "skip"]
    summary: str
    strengths: list[str]
    gaps: list[str]
    role_description: str
    company_description: str
    application_advice: str

class JobListing(BaseModel):
    title: str
    company: str
    description: str
    source: str
    url: str
    location: str | None = None
    country: str | None = None
    job_type: Literal["remote", "onsite", "hybrid", "unknown"] = "unknown"


class KeyWordAnalysisResult(BaseModel):
    keyword_score: int = Field(ge=0)
    matched_core_keywords: list[str]
    matched_supporting_keywords: list[str]
    passed_gate: bool


class SavedMatch(BaseModel):
    job: JobListing
    keyword_analysis: KeyWordAnalysisResult
    ai_analysis: AIAnalysis | None = None
    ai_error: str | None = None