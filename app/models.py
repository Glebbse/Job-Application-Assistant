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

