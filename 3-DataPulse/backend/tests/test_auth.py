"""Authentication tests - IMPLEMENTED."""

import pytest


def test_register_success(client):
    resp = client.post("/api/auth/register", json={
        "email": "new@example.com", "password": "pass123", "full_name": "New User"})
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_success(client):
    # Register first
    client.post("/api/auth/register", json={
        "email": "login@example.com", "password": "pass123", "full_name": "Login User"})
    # Then login
    resp = client.post("/api/auth/login", json={
        "email": "login@example.com", "password": "pass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/auth/register", json={
        "email": "wrong@example.com", "password": "pass123", "full_name": "Wrong User"})
    resp = client.post("/api/auth/login", json={
        "email": "wrong@example.com", "password": "badpass"})
    assert resp.status_code == 401
