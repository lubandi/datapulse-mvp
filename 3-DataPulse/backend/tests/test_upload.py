"""Upload tests - IMPLEMENTED."""

import io
import pytest


def test_upload_csv_success(client):
    """Test uploading a valid CSV file."""
    csv_content = "id,name,age
1,Alice,30
2,Bob,25
3,Carol,35
"
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    resp = client.post("/api/datasets/upload", files=files)
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test"
    assert data["file_type"] == "csv"
    assert data["row_count"] == 3
    assert data["column_count"] == 3
    assert data["status"] == "PENDING"
