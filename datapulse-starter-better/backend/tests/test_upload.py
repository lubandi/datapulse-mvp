"""Upload tests — now requires authentication."""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
def test_upload_csv_success(auth_client):
    """Test uploading a valid CSV file with authentication."""
    csv_content = b"id,name,age\n1,Alice,30\n2,Bob,25\n3,Carol,35\n"
    uploaded = SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")
    resp = auth_client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test"
    assert data["file_type"] == "csv"
    assert data["row_count"] == 3
    assert data["column_count"] == 3
    assert data["status"] == "PENDING"


@pytest.mark.django_db
def test_upload_json_success(auth_client):
    """Test uploading a valid JSON file."""
    import json
    json_data = json.dumps([
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]).encode()
    uploaded = SimpleUploadedFile("test.json", json_data, content_type="application/json")
    resp = auth_client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    assert resp.status_code == 201
    data = resp.json()
    assert data["file_type"] == "json"
    assert data["row_count"] == 2


@pytest.mark.django_db
def test_upload_unsupported_format(auth_client):
    """Test that non-CSV/JSON files are rejected."""
    uploaded = SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")
    resp = auth_client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_upload_no_file(auth_client):
    """Test upload with no file attached."""
    resp = auth_client.post("/api/datasets/upload", {}, format="multipart")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_list_datasets(auth_client):
    """Test listing datasets after upload."""
    csv_content = b"id,name\n1,Alice\n"
    uploaded = SimpleUploadedFile("list_test.csv", csv_content, content_type="text/csv")
    auth_client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")

    resp = auth_client.get("/api/datasets/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.django_db
def test_upload_unauthenticated(client):
    """Upload should require authentication."""
    csv_content = b"id,name\n1,Alice\n"
    uploaded = SimpleUploadedFile("noauth.csv", csv_content, content_type="text/csv")
    resp = client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    assert resp.status_code == 401
