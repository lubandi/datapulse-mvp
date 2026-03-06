from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class CheckResultResponse(BaseModel):
    id: int
    dataset_id: int
    rule_id: int
    passed: bool
    failed_rows: int
    total_rows: int
    details: Optional[str] = None
    checked_at: datetime
    class Config:
        from_attributes = True

class QualityScoreResponse(BaseModel):
    id: int
    dataset_id: int
    score: float
    total_rules: int
    passed_rules: int
    failed_rules: int
    checked_at: datetime
    class Config:
        from_attributes = True

class QualityReport(BaseModel):
    dataset_id: int
    dataset_name: str
    score: float
    total_rules: int
    results: List[CheckResultResponse]
    checked_at: datetime
