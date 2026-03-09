import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

@pytest.mark.django_db
def test_create_rule_empty_params(auth_client):
    """Verify that rules can be created with empty dataset_type and parameters."""
    resp = auth_client.post(
        "/api/rules/",
        {
            "name": "Wildcard Rule",
            "rule_type": "NOT_NULL",
            "field_name": "name",
            "severity": "HIGH",
            "dataset_type": "",
            "parameters": "",
        },
        format="json",
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["dataset_type"] == ""
    assert data["parameters"] == ""

@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_wildcard_rule_applied(auth_client, sample_csv_content):
    """Verify that a rule with empty dataset_type is applied to all datasets."""
    # 1. Create wildcard rule
    rule_resp = auth_client.post(
        "/api/rules/",
        {
            "name": "Wildcard Not Null",
            "rule_type": "NOT_NULL",
            "field_name": "name",
            "severity": "HIGH",
            "dataset_type": "",
            "parameters": "",
        },
        format="json",
    )
    rule_id = rule_resp.json()["id"]

    # 2. Upload CSV
    uploaded = SimpleUploadedFile("test.csv", sample_csv_content, content_type="text/csv")
    upload_resp = auth_client.post("/api/datasets/upload", {"file": uploaded}, format="multipart")
    dataset_id = upload_resp.json()["id"]

    # 3. Run checks
    resp = auth_client.post(f"/api/checks/run/{dataset_id}")
    assert resp.status_code == 200
    
    # 4. Verify results include our wildcard rule_id
    results_resp = auth_client.get(f"/api/checks/results/{dataset_id}")
    results = results_resp.json()
    rule_ids = [r["rule_id"] for r in results]
    assert rule_id in rule_ids
