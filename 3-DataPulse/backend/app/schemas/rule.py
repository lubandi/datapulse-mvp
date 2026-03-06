from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RuleCreate(BaseModel):
    name: str
    dataset_type: str
    field_name: str
    rule_type: str
    parameters: Optional[str] = None
    severity: str = "MEDIUM"

class RuleResponse(BaseModel):
    id: int
    name: str
    dataset_type: str
    field_name: str
    rule_type: str
    parameters: Optional[str] = None
    severity: str
    is_active: bool
    created_at: datetime
    class Config:
        from_attributes = True

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    dataset_type: Optional[str] = None
    field_name: Optional[str] = None
    rule_type: Optional[str] = None
    parameters: Optional[str] = None
    severity: Optional[str] = None
    is_active: Optional[bool] = None
