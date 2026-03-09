"""Test fixtures for pytest-django."""

import io
import json

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

VALID_PASSWORD = "TestPass1!"


@pytest.fixture
def client():
    """Return a DRF APIClient for making test requests."""
    return APIClient()


@pytest.fixture
def sample_user(client):
    """Register a test user and return the response data."""
    resp = client.post(
        "/api/auth/register",
        {
            "email": "test@example.com",
            "password": VALID_PASSWORD,
            "full_name": "Test User",
        },
        format="json",
    )
    return resp.json()


@pytest.fixture
def auth_token(sample_user):
    """Return the access token from sample_user registration."""
    return sample_user["access_token"]


@pytest.fixture
def auth_client(client, auth_token):
    """Return an APIClient with JWT auth header set."""
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
    return client


@pytest.fixture
def sample_csv_content():
    """Return sample CSV bytes for testing."""
    return b"id,name,age,email\n1,Alice,30,alice@test.com\n2,Bob,25,bob@test.com\n3,Carol,35,carol@test.com\n"


@pytest.fixture
def uploaded_dataset(auth_client, sample_csv_content):
    """Upload a CSV file and return the dataset response data."""
    uploaded = SimpleUploadedFile("test.csv", sample_csv_content, content_type="text/csv")
    resp = auth_client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture
def sample_rule(auth_client, uploaded_dataset):
    """Create a validation rule and return its data."""
    resp = auth_client.post(
        "/api/rules/",
        {
            "name": "Not Null Check - name",
            "rule_type": "NOT_NULL",
            "field_name": "name",
            "severity": "HIGH",
            "dataset_type": "csv",
            "parameters": "{}",
        },
        format="json",
    )
    assert resp.status_code == 201
    return resp.json()
