from typing import Any

from pydantic import BaseModel, Field


class GenerateResumeRequest(BaseModel):
    target_position: str
    personal_info: str = ""
    basics: dict[str, Any] = Field(default_factory=dict)
    education: str = ""
    skills: list[str] = Field(default_factory=list)
    projects: str = ""
    work: str = ""
    awards: str = ""
    expected_location: str = ""
    expected_salary: str = ""
    status: str = ""
    style: str = "技术型"


class ScoreResumeRequest(BaseModel):
    resume_data: dict[str, Any]
    target_position: str = ""
    job_description: str = ""


class OptimizeSectionRequest(BaseModel):
    section_type: str
    section_title: str
    section_content: Any
    full_resume_data: dict[str, Any] = Field(default_factory=dict)
    target_position: str = ""
    job_description: str = ""
    optimize_style: str = "更专业"


class OptimizeResumeRequest(BaseModel):
    resume_data: dict[str, Any]
    target_position: str = ""
    job_description: str = ""
    optimize_style: str = "更适合技术岗"


class JdOptimizeRequest(BaseModel):
    resume_data: dict[str, Any]
    job_description: str


class SummaryGenerateRequest(BaseModel):
    resume_data: dict[str, Any]
    target_position: str = ""


class ProjectOptimizeRequest(BaseModel):
    project: dict[str, Any]
    target_position: str = ""
    job_description: str = ""
