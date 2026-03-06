"""Authentication tests — registration, login, and protection."""

import pytest

VALID_PASSWORD = "TestPass1!"


@pytest.mark.django_db
def test_register_success(client):
    resp = client.post(
        "/api/auth/register",
        {"email": "new@example.com", "password": VALID_PASSWORD, "full_name": "New User"},
        format="json",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.django_db
def test_register_weak_password_rejected(client):
    resp = client.post(
        "/api/auth/register",
        {"email": "weak@example.com", "password": "short", "full_name": "Weak User"},
        format="json",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_duplicate_email(client):
    client.post(
        "/api/auth/register",
        {"email": "dup@example.com", "password": VALID_PASSWORD, "full_name": "First"},
        format="json",
    )
    resp = client.post(
        "/api/auth/register",
        {"email": "dup@example.com", "password": VALID_PASSWORD, "full_name": "Second"},
        format="json",
    )
    assert resp.status_code == 400


@pytest.mark.django_db
def test_login_success(client):
    client.post(
        "/api/auth/register",
        {"email": "login@example.com", "password": VALID_PASSWORD, "full_name": "Login User"},
        format="json",
    )
    resp = client.post(
        "/api/auth/login",
        {"email": "login@example.com", "password": VALID_PASSWORD},
        format="json",
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.django_db
def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        {"email": "wrong@example.com", "password": VALID_PASSWORD, "full_name": "Wrong User"},
        format="json",
    )
    resp = client.post(
        "/api/auth/login",
        {"email": "wrong@example.com", "password": "BadPass1!"},
        format="json",
    )
    assert resp.status_code == 401


@pytest.mark.django_db
def test_protected_endpoint_rejects_unauthenticated(client):
    """Verify that protected endpoints require JWT auth."""
    resp = client.get("/api/datasets/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_protected_endpoint_accepts_authenticated(auth_client):
    """Verify that protected endpoints work with JWT auth."""
    resp = auth_client.get("/api/datasets/")
    assert resp.status_code == 200
