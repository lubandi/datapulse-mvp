"""Quality checks router - STUB: All endpoints need implementation."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.report import CheckResultResponse, QualityScoreResponse

router = APIRouter()


@router.post("/run/{dataset_id}", status_code=200)
def run_checks(dataset_id: int, db: Session = Depends(get_db)):
    """Run all applicable validation checks on a dataset.

    TODO: Implement this endpoint.

    Steps:
    1. Fetch dataset by ID (404 if not found)
    2. Get DatasetFile, read file path
    3. Load file with file_parser (parse_csv or parse_json)
    4. Fetch active ValidationRules matching dataset type
    5. Init ValidationEngine, call run_all_checks(df, rules)
    6. Create CheckResult records for each check
    7. Calculate quality score via scoring_service
    8. Create QualityScore record
    9. Update dataset status (VALIDATED or FAILED)
    10. Return score and results summary
    """
    raise HTTPException(status_code=501, detail="POST /api/checks/run not implemented")


@router.get("/results/{dataset_id}", response_model=list[CheckResultResponse])
def get_check_results(dataset_id: int, db: Session = Depends(get_db)):
    """Get all check results for a dataset.

    TODO: Implement this endpoint.

    Steps:
    1. Query CheckResult table by dataset_id
    2. Order by checked_at descending
    3. Return list of results
    """
    raise HTTPException(status_code=501, detail="GET /api/checks/results not implemented")
