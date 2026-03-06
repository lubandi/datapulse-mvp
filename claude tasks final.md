# DataPulse Backend — Task Checklist

> Tasks organized **chronologically** (dependencies first) and tagged by developer role from the project description. We are implementing everything, but each task is labeled so it maps to the original role-specific deliverables.

---

## Phase 1 — Foundational Fixes & Hardening

> Issues discovered during audit that affect all downstream work.

- [ ] **Fix [conftest.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/tests/conftest.py) test password** — current `"test123"` fails the password validator. Use a valid password. *(Cross-cutting)*
- [ ] **Enforce `IsAuthenticated` on protected views** — `datasets`, `rules`, [checks](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#11-32), `reports` views should require JWT auth. Auth views stay `AllowAny`. *(Backend Dev 2 — Auth System)*
- [ ] **Set `uploaded_by` on Dataset upload** — [datasets/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datasets/views.py) never associates the authenticated user with the dataset. *(Backend Dev 1 — File Upload)*
- [ ] **Add `role` field to User model** — project specifies ADMIN/USER roles with default credentials. Add `role` field + migration + seed data. *(Backend Dev 2 — Auth/Schema)*

---

## Phase 2 — Backend Developer 1: Validation Engine & Rule Management

> Core business logic. Must be done before checks/reports can work.

- [x] File Upload API (`POST /api/datasets/upload`) — ✅ done
- [x] File Listing API (`GET /api/datasets`) — ✅ done
- [x] File Parsing (CSV/JSON via Pandas) — ✅ done
- [x] Rule Create API (`POST /api/rules`) — ✅ done
- [x] Rule List API (`GET /api/rules`) — ✅ done
- [x] [null_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#33-45) in [ValidationEngine](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#8-95) — ✅ done
- [ ] **[type_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#46-58)** — [checks/services/validation_engine.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py)
- [ ] **[range_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#59-70)** — [checks/services/validation_engine.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py)
- [ ] **[unique_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#71-82)** — [checks/services/validation_engine.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py)
- [ ] **[regex_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#83-95)** — [checks/services/validation_engine.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py)
- [ ] **Quality Score Calculator** — [checks/services/scoring_service.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/scoring_service.py)
- [ ] **Rule Update API** — `PUT /api/rules/{id}` in [rules/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/rules/views.py)
- [ ] **Rule Delete API** — `DELETE /api/rules/{id}` (soft-delete) in [rules/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/rules/views.py)

---

## Phase 3 — Backend Developer 1 + 2: Checks & Reports API

> Depends on Phase 2 (validation engine + scoring).

- [ ] **Run Checks endpoint** — `POST /api/checks/run/{dataset_id}` in [checks/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/views.py)
- [ ] **Check Results endpoint** — `GET /api/checks/results/{dataset_id}` in [checks/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/views.py)
- [ ] **Report Service: [generate_report()](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py#4-18)** — [reports/services/report_service.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py)
- [ ] **Report Service: [get_trend_data()](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py#20-33)** — [reports/services/report_service.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py)
- [ ] **Quality Report API** — `GET /api/reports/{dataset_id}` in [reports/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/views.py)
- [ ] **Quality Trends API** — `GET /api/reports/trends` in [reports/views.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/views.py)
- [ ] **Dashboard Aggregate API** — ⚠️ GAP: new `GET /api/reports/dashboard` returning latest scores per dataset

---

## Phase 4 — Backend Developer 3: Scheduling & Notifications (Stretch Goals)

> Only after all MVP phases are complete. Requires new infrastructure.

- [ ] **Scheduled Checks** — `django-celery-beat` + Celery task for auto quality checks
- [ ] **Notification System** — Email alerts when score drops below configurable threshold
- [ ] **Batch Processing** — `POST /api/checks/run-batch` for multiple datasets
- [ ] **Audit Log** — New model tracking who ran what check and when
- [ ] **Configuration API** — CRUD for schedules and alert thresholds

---

## Phase 5 — Testing & Verification

> Runs alongside Phases 2–4 but final verification is here.

- [ ] Unit tests for [ValidationEngine](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#8-95) (all 5 check types + edge cases)
- [ ] Unit tests for `scoring_service` (weighted scoring)
- [ ] API tests for `rules` PUT/DELETE
- [ ] API tests for [checks](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#11-32) run + results
- [ ] API tests for `reports` report + trends + dashboard
- [ ] Integration test: register → upload CSV → create rules → run checks → get report → view trends
- [ ] All tests pass with `pytest -v`
