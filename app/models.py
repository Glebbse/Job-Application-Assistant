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
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    publication_date: str | None = None
    salary: str | None = None


class KeyWordAnalysisResult(BaseModel):
    keyword_score: int = Field(ge=0)
    matched_required_keywords: list[str]
    matched_preferred_keywords: list[str]
    matched_supporting_keywords: list[str]
    passed_gate: bool
    rejection_reason: str | None = None


class SavedMatch(BaseModel):
    job: JobListing
    keyword_analysis: KeyWordAnalysisResult
    ai_analysis: AIAnalysis | None = None
    ai_error: str | None = None


class RunSummary(BaseModel):
    fetched_jobs: int
    filtered_jobs: int
    ai_analyzed: int
    apply_count: int
    maybe_count: int
    skip_count: int
    error_count: int


class RunMetaData(BaseModel):
    started_at: str
    source: str
    country: str | None = None
    target_apply_count: int # goal to have applied jobs per day


class RunResult(BaseModel):
    run: RunMetaData
    summary: RunSummary
    countries: list[str]


class FetchedJobsBatches(BaseModel):
    source: str
    country: str | None = None
    fetched_jobs: list[JobListing]
    filtered_jobs: list[JobListing]
    jobs_path: str