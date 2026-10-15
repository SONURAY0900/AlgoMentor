from fastapi import APIRouter, HTTPException

from llm.client import LLMError
from orchestrator.orchestrator import PipelineError, run_pipeline
from schemas.request_schema import AnalyzeRequest
from schemas.response_schema import AnalyzeResponse

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    """
    Entry API for code/problem analysis
    """
    try:
        return run_pipeline(request)
    except PipelineError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except LLMError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
