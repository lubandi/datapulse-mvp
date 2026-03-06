# DataPulse Backend — Implementation Plan (v3)

Complete the Django backend for DataPulse. Tasks are **chronologically ordered** (dependencies first) and tagged by developer role.

---

## Gap Analysis (Full Codebase Audit)

> [!IMPORTANT]
> Beyond the explicit TODO stubs, the audit revealed **4 bugs/gaps in existing "done" code** and **5 missing deliverables**.

### Bugs in Existing Code

| # | Issue | File | Impact |
|---|-------|------|--------|
| 1 | **All views use `AllowAny`** — no JWT enforcement on protected endpoints | [settings/base.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datapulse/settings/base.py) (global default) | Anyone can upload, create rules, run checks without logging in |
| 2 | **`uploaded_by` is never set** on dataset creation | `datasets/views.py:59-66` | Datasets have no owner; can't filter by user |
| 3 | **Test fixture password fails validation** — `"test123"` doesn't meet uppercase/digit/special requirements | `tests/conftest.py:18` | All tests using [sample_user](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/tests/conftest.py#13-22) fixture will fail |
| 4 | **No `role` field on User** — project requires ADMIN/USER roles with default credentials | [authentication/models.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/authentication/models.py) | No way to distinguish admin from regular user |

### Missing Deliverables

| # | Gap | Developer Role | Priority |
|---|-----|---------------|----------|
| 5 | Dashboard Aggregate API (latest scores for all datasets) | Backend Dev 2 | **MVP** |
| 6 | Scheduled Checks (cron-based) | Backend Dev 3 | Stretch |
| 7 | Email Notifications (quality drop alerts) | Backend Dev 3 | Stretch |
| 8 | Batch Processing (multi-dataset checks) | Backend Dev 3 | Stretch |
| 9 | Audit Log + Configuration API | Backend Dev 3 | Stretch |

---

## Phase 1 — Foundational Fixes *(Backend Dev 2: Auth/Schema)*

These must be fixed first as they affect all downstream work.

#### [MODIFY] [conftest.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/tests/conftest.py)
- Change test password from `"test123"` to something passing the validator (e.g. `"TestPass1!"`)

#### [MODIFY] [views.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datasets/views.py) *(Backend Dev 1)*
- In `DatasetUploadView.post`, set `uploaded_by=request.user` when user is authenticated

#### [MODIFY] [base.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datapulse/settings/base.py)
- Change `DEFAULT_PERMISSION_CLASSES` from `AllowAny` to `IsAuthenticated`
- Auth views already explicitly set `AllowAny` via throttle — add explicit `permission_classes = [AllowAny]`

#### [MODIFY] [models.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/authentication/models.py)
- Add `role = models.CharField(max_length=10, default="USER")` with choices `ADMIN`/`USER`
- Create migration
- Add management command or migration to seed default ADMIN and USER accounts from project spec

#### [MODIFY] [views.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/authentication/views.py)
- Add `permission_classes = [AllowAny]` explicitly to [RegisterView](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/authentication/views.py#14-42) and [LoginView](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/authentication/views.py#44-72)

---

## Phase 2 — Validation Engine & Rules CRUD *(Backend Dev 1)*

Core business logic. Everything in Phase 3 depends on this.

#### [MODIFY] [validation_engine.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py)

| Method | Approach |
|--------|----------|
| [type_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#46-58) | `pd.to_numeric()` / `pd.to_datetime()` / `.astype()` with `errors='coerce'`, count NaN conversions |
| [range_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#59-70) | `pd.to_numeric(errors='coerce')`, count rows where `value < min` or `value > max` |
| [unique_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#71-82) | `df[field].duplicated()`, count `True` values |
| [regex_check](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#83-95) | `df[field].astype(str).str.fullmatch(pattern)`, count `False` values |

All methods handle "field not found" → `{passed: False, failed_rows: total, details: "Field X not found"}`.

#### [MODIFY] [scoring_service.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/scoring_service.py)

Weighted scoring:
```
score = (sum of weights for passing checks) / (sum of all weights) × 100
```
Where weights: `HIGH=3, MEDIUM=2, LOW=1`.

#### [MODIFY] [views.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/rules/views.py) (Rules)

- **`PUT`**: Fetch rule → validate with [RuleUpdateSerializer](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/rules/serializers.py#27-35) → update non-null fields → validate `rule_type`/`severity` → save → 200
- **`DELETE`**: Fetch rule → set `is_active=False` → save → 204

---

## Phase 3 — Checks & Reports API *(Backend Dev 1 + Backend Dev 2)*

#### [MODIFY] [views.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/views.py)

**`RunChecksView.post`** — 10-step orchestration:
1. Fetch [Dataset](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datasets/models.py#6-25) by ID → 404 if missing
2. Get [DatasetFile](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datasets/models.py#27-36) → read file path
3. Parse with [parse_csv](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datasets/services/file_parser.py#6-16) / [parse_json](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/datasets/services/file_parser.py#18-28) (based on `file_type`)
4. Query `ValidationRule.objects.filter(is_active=True, dataset_type=dataset.file_type)`
5. Instantiate [ValidationEngine](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#8-95), call [run_all_checks(df, rules)](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/validation_engine.py#11-32)
6. Bulk create [CheckResult](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/models.py#6-19) rows
7. Call [calculate_quality_score(results, rules)](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/services/scoring_service.py#4-31) → create [QualityScore](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/models.py#21-33)
8. Update `dataset.status` → `"VALIDATED"` or `"FAILED"` (based on score threshold)
9. Return serialized [QualityScore](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/models.py#21-33)

**`CheckResultsView.get`**: `CheckResult.objects.filter(dataset_id=...).order_by('-checked_at')` → serialize → return

#### [MODIFY] [report_service.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py) *(Backend Dev 2)*

- **[generate_report(dataset_id)](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py#4-18)**: Fetch dataset → latest [QualityScore](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/models.py#21-33) → [CheckResult](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/models.py#6-19) entries → bundle into [QualityReport](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/serializers.py#7-14) dict
- **[get_trend_data(days)](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py#20-33)**: `QualityScore.objects.filter(checked_at__gte=start).order_by('checked_at')` with dataset info

#### [MODIFY] [views.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/views.py) *(Backend Dev 2)*

- **`DatasetReportView.get`**: Call [generate_report()](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py#4-18) → serialize → 200 (or 404)
- **`QualityTrendsView.get`**: Parse `?days=30` → call [get_trend_data()](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/services/report_service.py#20-33) → serialize → 200

#### ⚠️ NEW: Dashboard Aggregate *(Backend Dev 2)*

#### [MODIFY] [views.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/views.py)
- Add `DashboardView` returning latest [QualityScore](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/models.py#21-33) per dataset using Django `Subquery`/`OuterRef`

#### [MODIFY] [urls.py](file:///C:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/reports/urls.py)
- Add `path("dashboard", DashboardView.as_view())`

---

## Phase 4 — Scheduling & Notifications *(Backend Dev 3 — Stretch Goals)*

> [!WARNING]
> Only attempt after MVP is complete and tested. Requires adding `celery`, `django-celery-beat`, and `redis` to the stack.

1. **Scheduled Checks**: Celery task wrapping the [RunChecksView](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/checks/views.py#11-40) logic, triggered by `django-celery-beat`
2. **Notifications**: Django email backend + check score against threshold post-run
3. **Batch Processing**: New `POST /api/checks/run-batch` accepting `{dataset_ids: [...]}`
4. **Audit Log**: New `AuditLog` model ([user](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/authentication/models.py#10-18), `action`, `dataset_id`, `timestamp`, `details`)
5. **Configuration API**: New `ScheduleConfig` / `AlertConfig` models + CRUD views

---

## Phase 5 — Testing & Verification

### Automated Tests

| Test File | Covers | Phase |
|-----------|--------|-------|
| [tests/test_auth.py](file:///c:/Users/Amalitech/Desktop/locked_in/z_data_pulse_me/datapulse-starter-better/backend/tests/test_auth.py) | Existing auth tests (update password) | 1 |
| `tests/test_rules.py` | PUT, DELETE, validation errors | 2 |
| `tests/test_validation_engine.py` | All 5 check types with edge cases | 2 |
| `tests/test_scoring.py` | Weighted score calculation | 2 |
| `tests/test_checks.py` | Run checks + results endpoints | 3 |
| `tests/test_reports.py` | Report + trends + dashboard | 3 |
| `tests/test_integration.py` | Full end-to-end flow | 3 |

```bash
cd backend && pytest -v
```

### Manual Verification
1. `docker-compose up --build`
2. Swagger UI at `http://localhost:8000/docs/`
3. Full flow: register → login → upload CSV → create rules → run checks → view report → view trends → dashboard
