"""API routes for the codebase explainer."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Optional
import shutil
from pathlib import Path

from app.models.schemas import (
    AnalyzeRequest, AnalysisResponse, GenerateReadmeRequest,
    GenerateReadmeResponse, AskQuestionRequest, AskQuestionResponse,
    ErrorResponse
)
from app.services.repo_service import RepoService
from app.services.gemini_service import GeminiService

router = APIRouter()

# Service instances
repo_service = RepoService()
gemini_service = GeminiService()

# In-memory cache for analysis results (simple implementation)
# In production, consider Redis or similar
_analysis_cache: Dict[str, Dict] = {}


def _cleanup_repo(repo_path: str):
    """Background task to cleanup repository directory."""
    try:
        path = Path(repo_path)
        if path.exists():
            # Remove parent directory (temp directory containing the repo)
            parent = path.parent
            if parent.exists():
                shutil.rmtree(parent, ignore_errors=True)
    except Exception:
        pass


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
):
    """
    Analyze a GitHub repository and return architecture, structure, API flow, and DB models.
    """
    try:
        # Analyze repository
        repo_data = repo_service.analyze_repo(request.repo_url, request.branch)
        
        if repo_data['total_files'] == 0:
            return AnalysisResponse(
                architecture="No code files found in repository.",
                folder_structure=repo_data['tree_structure'] or "No structure available.",
                api_flow="No API information available.",
                db_models="No database information available.",
                repo_url=request.repo_url,
                total_files=0,
                total_chars=0
            )
        
        # Get AI analysis
        analysis = gemini_service.analyze_codebase(
            repo_data['tree_structure'],
            repo_data['files']
        )
        
        # Store in cache for later use
        cache_key = request.repo_url
        _analysis_cache[cache_key] = {
            'analysis': analysis,
            'tree_structure': repo_data['tree_structure'],
            'files': repo_data['files'],
            'repo_url': request.repo_url
        }
        
        # Schedule cleanup
        background_tasks.add_task(_cleanup_repo, repo_data['repo_path'])
        
        return AnalysisResponse(
            architecture=analysis['architecture'],
            folder_structure=analysis['folder_structure'],
            api_flow=analysis['api_flow'],
            db_models=analysis['db_models'],
            repo_url=request.repo_url,
            total_files=repo_data['total_files'],
            total_chars=repo_data['total_chars']
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/generate-readme", response_model=GenerateReadmeResponse)
async def generate_readme(request: GenerateReadmeRequest):
    """
    Generate a README.md file for the repository.
    Can use cached analysis or re-analyze if repo_url provided.
    """
    try:
        # Determine if we need to fetch from cache or re-analyze
        if request.analysis:
            # Use provided analysis
            analysis = request.analysis
            cache_key = request.repo_url or "unknown"
            
            # Try to get cached data
            if cache_key in _analysis_cache:
                cached = _analysis_cache[cache_key]
                tree_structure = cached['tree_structure']
                files = cached['files']
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Analysis provided but no cached repository data. Please call /analyze first or provide repo_url."
                )
        elif request.repo_url:
            # Re-analyze or use cache
            cache_key = request.repo_url
            if cache_key in _analysis_cache:
                cached = _analysis_cache[cache_key]
                analysis = cached['analysis']
                tree_structure = cached['tree_structure']
                files = cached['files']
            else:
                # Need to analyze first
                repo_data = repo_service.analyze_repo(request.repo_url)
                analysis = gemini_service.analyze_codebase(
                    repo_data['tree_structure'],
                    repo_data['files']
                )
                tree_structure = repo_data['tree_structure']
                files = repo_data['files']
                
                # Cache it
                _analysis_cache[cache_key] = {
                    'analysis': analysis,
                    'tree_structure': tree_structure,
                    'files': files,
                    'repo_url': request.repo_url
                }
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'repo_url' or 'analysis' must be provided."
            )
        
        # Generate README
        readme = gemini_service.generate_readme(analysis, tree_structure, files)
        
        return GenerateReadmeResponse(
            readme=readme,
            repo_url=request.repo_url or cache_key
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(request: AskQuestionRequest):
    """
    Ask a question about the codebase.
    Can use cached analysis or re-analyze if repo_url provided.
    """
    try:
        # Determine if we need to fetch from cache or re-analyze
        if request.analysis:
            # Use provided analysis
            analysis = request.analysis
            cache_key = request.repo_url or "unknown"
            
            # Try to get cached data
            if cache_key in _analysis_cache:
                cached = _analysis_cache[cache_key]
                tree_structure = cached['tree_structure']
                files = cached['files']
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Analysis provided but no cached repository data. Please call /analyze first or provide repo_url."
                )
        elif request.repo_url:
            # Re-analyze or use cache
            cache_key = request.repo_url
            if cache_key in _analysis_cache:
                cached = _analysis_cache[cache_key]
                analysis = cached['analysis']
                tree_structure = cached['tree_structure']
                files = cached['files']
            else:
                # Need to analyze first
                repo_data = repo_service.analyze_repo(request.repo_url)
                analysis = gemini_service.analyze_codebase(
                    repo_data['tree_structure'],
                    repo_data['files']
                )
                tree_structure = repo_data['tree_structure']
                files = repo_data['files']
                
                # Cache it
                _analysis_cache[cache_key] = {
                    'analysis': analysis,
                    'tree_structure': tree_structure,
                    'files': files,
                    'repo_url': request.repo_url
                }
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'repo_url' or 'analysis' must be provided."
            )
        
        # Answer question
        answer = gemini_service.answer_question(
            request.question,
            tree_structure,
            files,
            analysis
        )
        
        return AskQuestionResponse(
            answer=answer,
            question=request.question,
            repo_url=request.repo_url or cache_key
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
