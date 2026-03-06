"""Integration test — full end-to-end flow:
Register → Upload CSV → Create rules → Run checks → Get report → View trends.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile


VALID_PASSWORD = "IntegTest1!"


@pytest.mark.django_db
def test_full_e2e_flow(client):
    """End-to-end: register → upload → rules → checks → report → trends."""

    # 1. Register
    reg_resp = client.post(
        "/api/auth/register",
        {"email": "e2e@example.com", "password": VALID_PASSWORD, "full_name": "E2E User"},
        format="json",
    )
    assert reg_resp.status_code == 201
    token = reg_resp.json()["access_token"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # 2. Upload CSV
    csv_content = (
        b"id,name,age,email\n"
        b"1,Alice,30,alice@test.com\n"
        b"2,Bob,25,bob@test.com\n"
        b"3,,35,carol@test.com\n"  # name is null on purpose
        b"4,Dave,150,not-an-email\n"  # age out of range, email invalid
        b"5,Eve,28,eve@test.com\n"
    )
    uploaded = SimpleUploadedFile("e2e.csv", csv_content, content_type="text/csv")
    upload_resp = client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    assert upload_resp.status_code == 201
    dataset_id = upload_resp.json()["id"]
    assert upload_resp.json()["row_count"] == 5

    # 3. Create rules
    rules_to_create = [
        {
            "name": "Name not null",
            "rule_type": "NOT_NULL",
            "field_name": "name",
            "severity": "HIGH",
            "dataset_type": "csv",
            "parameters": "{}",
        },
        {
            "name": "Age range",
            "rule_type": "RANGE",
            "field_name": "age",
            "severity": "MEDIUM",
            "dataset_type": "csv",
            "parameters": '{"min": 0, "max": 120}',
        },
        {
            "name": "Email format",
            "rule_type": "REGEX",
            "field_name": "email",
            "severity": "LOW",
            "dataset_type": "csv",
            "parameters": '{"pattern": ".+@.+\\\\..+"}',
        },
    ]

    for rule_data in rules_to_create:
        resp = client.post("/api/rules/", rule_data, format="json")
        assert resp.status_code == 201

    # Verify rules created
    rules_resp = client.get("/api/rules/")
    assert rules_resp.status_code == 200
    assert len(rules_resp.json()) == 3

    # 4. Run checks
    check_resp = client.post(f"/api/checks/run/{dataset_id}")
    assert check_resp.status_code == 200
    score_data = check_resp.json()
    assert "score" in score_data
    assert score_data["total_rules"] == 3
    # We expect some failures: null name (row 3), age>120 (row 4), bad email (row 4)
    assert score_data["failed_rules"] >= 1

    # 5. Get check results
    results_resp = client.get(f"/api/checks/results/{dataset_id}")
    assert results_resp.status_code == 200
    results = results_resp.json()
    assert len(results) == 3  # one result per rule

    # 6. Get report
    report_resp = client.get(f"/api/reports/{dataset_id}")
    assert report_resp.status_code == 200
    report = report_resp.json()
    assert report["dataset_id"] == dataset_id
    assert "score" in report

    # 7. View trends
    trends_resp = client.get("/api/reports/trends?days=30")
    assert trends_resp.status_code == 200
    trends = trends_resp.json()
    assert len(trends) >= 1

    # 8. Dashboard
    dash_resp = client.get("/api/reports/dashboard")
    assert dash_resp.status_code == 200
    dashboard = dash_resp.json()
    assert len(dashboard) >= 1

    # 9. Verify dataset status was updated
    datasets_resp = client.get("/api/datasets/")
    assert datasets_resp.status_code == 200
    datasets = datasets_resp.json()
    e2e_dataset = next(d for d in datasets["datasets"] if d["id"] == dataset_id)
    assert e2e_dataset["status"] in ("VALIDATED", "FAILED")
