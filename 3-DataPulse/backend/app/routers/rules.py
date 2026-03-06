"""Validation rules router - PARTIAL implementation."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.rule import ValidationRule
from app.schemas.rule import RuleCreate, RuleResponse, RuleUpdate

router = APIRouter()

VALID_TYPES = {"NOT_NULL", "DATA_TYPE", "RANGE", "UNIQUE", "REGEX"}
VALID_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}


@router.post("", response_model=RuleResponse, status_code=201)
def create_rule(rule_data: RuleCreate, db: Session = Depends(get_db)):
    """Create a new validation rule - IMPLEMENTED."""
    if rule_data.rule_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid rule_type: {VALID_TYPES}")
    if rule_data.severity not in VALID_SEVERITIES:
        raise HTTPException(status_code=400, detail=f"Invalid severity: {VALID_SEVERITIES}")
    rule = ValidationRule(**rule_data.model_dump())
    db.add(rule); db.commit(); db.refresh(rule)
    return rule


@router.get("", response_model=list[RuleResponse])
def list_rules(dataset_type: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """List validation rules - IMPLEMENTED."""
    q = db.query(ValidationRule).filter(ValidationRule.is_active == True)
    if dataset_type:
        q = q.filter(ValidationRule.dataset_type == dataset_type)
    return q.all()


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: int, rule_data: RuleUpdate, db: Session = Depends(get_db)):
    """Update a validation rule - TODO: Implement.

    Steps:
    1. Fetch rule by ID (404 if not found)
    2. Update non-None fields from rule_data
    3. Validate rule_type and severity if changed
    4. Commit and return updated rule
    """
    raise HTTPException(status_code=501, detail="PUT /api/rules/{id} not implemented")


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Soft-delete a validation rule - TODO: Implement.

    Steps:
    1. Fetch rule by ID (404 if not found)
    2. Set is_active = False
    3. Commit, return 204
    """
    raise HTTPException(status_code=501, detail="DELETE /api/rules/{id} not implemented")
