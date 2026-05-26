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
    remote_id: int | None = None
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    publication_date: str | None = None
    salary: str | None = None


class KeyWordAnalysisResult(BaseModel):
    keyword_score: int = Field(ge=0)
    matched_required_keywords: list[str]
    matched_preferred_keywords: list[str]
    matched_supporting_keywords: list[str]
    matched_positive_title_keywords: bool
    passed_gate: bool
    rejection_reason: str | None = None


class SavedMatch(BaseModel):
    job: JobListing
    keyword_analysis: KeyWordAnalysisResult
    ai_analysis: AIAnalysis | None = None
    ai_error: str | None = None