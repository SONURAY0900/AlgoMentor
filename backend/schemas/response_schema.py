from pydantic import BaseModel
from typing import List, Optional


class Quality(BaseModel):
    is_correct: bool
    is_optimal: bool
    issues: List[str] = []


class Analysis(BaseModel):
    code_explanation: Optional[str] = None
    complexity: Optional[str] = None
    quality: Optional[Quality] = None
    root_cause: Optional[str] = None


class Classification(BaseModel):
    category: str
    data_structure: str
    strategy: str
    reason: str
    better_than_bruteforce: bool


class Solutions(BaseModel):
    bruteforce: Optional[str] = None
    optimal: Optional[str] = None


class AnalyzeResponse(BaseModel):
    mode: str
    language: str
    problem_statement: Optional[str] = None
    notes: List[str] = []

    analysis: Optional[Analysis] = None          # CODE mode only
    classification: Optional[Classification] = None
    solutions: Solutions
    solution_explanation: Optional[str] = None
    summary: Optional[str] = None
