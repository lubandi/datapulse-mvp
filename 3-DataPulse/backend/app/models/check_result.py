from datetime import datetime
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, Text
from app.database import Base

class CheckResult(Base):
    __tablename__ = "check_results"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    rule_id = Column(Integer, ForeignKey("validation_rules.id"), nullable=False)
    passed = Column(Boolean, nullable=False)
    failed_rows = Column(Integer, default=0)
    total_rows = Column(Integer, default=0)
    details = Column(Text, nullable=True)
    checked_at = Column(DateTime, default=datetime.utcnow)


class QualityScore(Base):
    __tablename__ = "quality_scores"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    score = Column(Float, nullable=False)
    total_rules = Column(Integer, default=0)
    passed_rules = Column(Integer, default=0)
    failed_rules = Column(Integer, default=0)
    checked_at = Column(DateTime, default=datetime.utcnow)
