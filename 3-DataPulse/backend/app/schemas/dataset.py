from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class DatasetResponse(BaseModel):
    id: int
    name: str
    file_type: str
    row_count: int
    column_count: int
    column_names: Optional[str] = None
    status: str
    uploaded_at: datetime
    class Config:
        from_attributes = True

class DatasetList(BaseModel):
    datasets: List[DatasetResponse]
    total: int
