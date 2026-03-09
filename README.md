# DataPulse

## Overview

**DataPulse** is an enterprise-grade data quality monitoring platform. It allows users to upload datasets, dynamically define validation rules, execute automated checks, and track data quality trends over time.

This project was migrating from a FastAPI starter template and is now fully implemented using a robust **Django + PostgreSQL + Celery** stack.

## Architecture

The system is composed of the following services (orchestrated via Docker Compose):
- **Backend API Server:** Django 4.2 API + Django REST Framework
- **Relational Database:** PostgreSQL 15 (Stores users, datasets, rules, and scoring results)
- **Background Task Broker:** Redis 7 (Message broker & backend for Celery)
- **Async Worker:** Celery (Handles asynchronous data processing and scheduled batch checks)
- **Scheduler:** Celery Beat (Triggers automated checks via crontab)

## Quick Start (Docker)

To run the entire stack locally in isolated containers:

1. **Install Docker Desktop**: If you haven't already, please download and install it from [docker.com](https://www.docker.com/products/docker-desktop/).
2. Open your terminal at the root of the project (where docker-compose.yml is) and run:
   ```bash
   docker-compose up --build
   ```

This will automatically spin up the database, cache, run all Django database migrations, seed the test users, and boot the backend API.

- **Interactive Swagger API Docs (Highly Recommended):** `http://localhost:8000/docs/`
- **API Base URL:** `http://localhost:8000`

> 💡 **Tip:** Use the Swagger documentation link above to explore all endpoints, view detailed request/response schemas, and test the API directly from your browser!

*(See `backend/README.md` for detailed instructions on local development, manual environment configurations, and testing).*

## API Endpoints (All Implemented ✅)

| Method | Endpoint                        | Description |
|--------|---------------------------------|-------------|
| POST   | `/api/auth/register`            | Register a new user |
| POST   | `/api/auth/login`               | Authenticate and receive a Bearer JWT |
| POST   | `/api/datasets/upload`          | Upload a new dataset (CSV/JSON) |
| GET    | `/api/datasets/`                | List user's datasets |
| POST   | `/api/rules/`                   | Create a custom validation rule |
| GET    | `/api/rules/`                   | List all validation rules |
| PUT    | `/api/rules/{id}`               | Update an existing rule |
| DELETE | `/api/rules/{id}`               | Soft-delete a rule |
| POST   | `/api/checks/run/{id}`          | Sync/Async validation check execution |
| GET    | `/api/checks/results/{id}`      | Get detailed row-level results |
| POST   | `/api/scheduling/batch`         | Async execution of rules across multiple datasets |
| GET    | `/api/reports/{id}`             | Retrieve dataset quality report metrics |
| GET    | `/api/reports/trends?days=30`   | Time-series reporting for checks |
| GET    | `/api/reports/dashboard`        | Dashboard aggregates |
| GET    | `/metrics/`                     | Prometheus application metrics exposition |

## Test Accounts

The stack comes pre-seeded with test accounts out-of-the-box:
- **Admin**: `admin@amalitech.com` (Password: `password123`)
- **User**: `user@amalitech.com` (Password: `password123`)

## Team Roles & Progress

### Backend (Completed ✅)
- Ported application from FastAPI to Django Rest Framework.
- Configured PostgreSQL, Celery, and Redis integration.
- Secured all endpoints using `SimpleJWT`.
- Built Pandas-driven validation engine (`NOT_NULL`, `DATA_TYPE`, `RANGE`, `UNIQUE`, `REGEX`).
- Implemented weighted scoring service.
- Implemented soft-delete rule structures.
- Completed full API coverage with >60 Pytest cases.

### Data Engineers / Frontend
- *(Pending implementation)* Define robust analytics schemas.
- *(Pending implementation)* Create Streamlit dashboards and visualization hooks.

### DevOps
- Converted infrastructure to single `docker-compose.yml`.
- Replaced base runtime commands with `entrypoint.sh` for robust migration sequencing.
- Established `.env` structure for production overriding.
