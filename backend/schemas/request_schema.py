from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    # Raw user input (code or problem); the backend decides which it is
    input: Optional[str] = None

    # Or send them explicitly
    code: Optional[str] = None
    problem: Optional[str] = None

    # Optional language (Python / Java / C / C++); None = auto
    language: Optional[str] = None
