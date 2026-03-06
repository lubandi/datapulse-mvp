"""Reports router - STUB: All endpoints need implementation."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.report import QualityReport, QualityScoreResponse

router = APIRouter()


@router.get("/{dataset_id}", response_model=QualityReport)
def get_dataset_report(dataset_id: int, db: Session = Depends(get_db)):
    """Get a full quality report for a dataset.

    TODO: Implement using report_service.generate_report().

    Steps:
    1. Fetch dataset by ID (404 if not found)
    2. Fetch latest QualityScore for this dataset
    3. Fetch all CheckResults from latest check run
    4. Compose QualityReport with dataset info, score, results
    5. Return the report
    """
    raise HTTPException(status_code=501, detail="GET /api/reports/{id} not implemented")


@router.get("/trends", response_model=list[QualityScoreResponse])
def get_quality_trends(days: int = Query(30, ge=1, le=365),
        db: Session = Depends(get_db)):
    """Get quality score trends over time.

    TODO: Implement using report_service.get_trend_data().

    Steps:
    1. Calculate start_date = now - days
    2. Query QualityScore after start_date
    3. Order by checked_at ascending
    4. Return scores showing quality trends
    """
    raise HTTPException(status_code=501, detail="GET /api/reports/trends not implemented")
