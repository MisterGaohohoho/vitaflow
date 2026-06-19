from typing import Any

from pydantic import BaseModel, Field


class ResumeGenerateResult(BaseModel):
    resume_data: dict[str, Any]
    template_id: str = "tech"
    template_config: dict[str, Any] = Field(default_factory=dict)
    explanation: str = ""


class ScoreDetail(BaseModel):
    dimension: str = "评分维度"
    score: int = 0
    max_score: int = 100
    comment: str = ""


class ResumeScoreResult(BaseModel):
    score: int
    level: str
    summary: str
    details: list[ScoreDetail] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class SectionOptimizeResult(BaseModel):
    optimized_section: Any
    changes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ProjectOptimizeResult(BaseModel):
    optimized_project: dict[str, Any]
    changes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class ResumeOptimizeResult(BaseModel):
    optimized_resume_data: dict[str, Any]
    summary: str = ""
    changes: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class JdOptimizeResult(BaseModel):
    job_keywords: dict[str, Any] = Field(default_factory=dict)
    match_analysis: dict[str, Any] = Field(default_factory=dict)
    optimized_resume_data: dict[str, Any]
    score: int = 0
    suggestions: list[str] = Field(default_factory=list)


class SummaryGenerateResult(BaseModel):
    content: str
    suggestions: list[str] = Field(default_factory=list)


class ResumeChatResult(BaseModel):
    reply: str
    suggestions: list[str] = Field(default_factory=list)
    optimized_resume_data: dict[str, Any] | None = None
