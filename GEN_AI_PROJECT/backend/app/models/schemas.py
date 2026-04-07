"""Pydantic schemas for request/response models."""
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, Dict, List


class AnalyzeRequest(BaseModel):
    """Request model for repository analysis."""
    repo_url: str = Field(..., description="GitHub repository URL")
    branch: Optional[str] = Field(None, description="Optional branch name (default: main/master)")


class AnalysisResponse(BaseModel):
    """Response model for repository analysis."""
    architecture: str
    folder_structure: str
    api_flow: str
    db_models: str
    repo_url: str
    total_files: int
    total_chars: int


class GenerateReadmeRequest(BaseModel):
    """Request model for README generation."""
    repo_url: Optional[str] = Field(None, description="GitHub repository URL (if not using cached analysis)")
    analysis: Optional[Dict[str, str]] = Field(None, description="Previous analysis result to reuse")


class GenerateReadmeResponse(BaseModel):
    """Response model for README generation."""
    readme: str
    repo_url: Optional[str] = None


class AskQuestionRequest(BaseModel):
    """Request model for Q&A."""
    repo_url: Optional[str] = Field(None, description="GitHub repository URL (if not using cached analysis)")
    analysis: Optional[Dict[str, str]] = Field(None, description="Previous analysis result to reuse")
    question: str = Field(..., description="Question about the codebase")


class AskQuestionResponse(BaseModel):
    """Response model for Q&A."""
    answer: str
    question: str
    repo_url: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
