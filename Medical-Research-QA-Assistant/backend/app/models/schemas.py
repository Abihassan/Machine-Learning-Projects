from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    question: str
    max_papers: int = 5

class SourceReference(BaseModel):
    pmid: str
    title: str
    snippet: str

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceReference]