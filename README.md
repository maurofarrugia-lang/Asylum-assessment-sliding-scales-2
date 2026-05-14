# Asylum Assessment App for Measuring Indiscriminate Violence

A production-oriented MVP for asylum and international protection casework. The application helps protection officers assess indiscriminate violence at country, region, district, and custom geographic levels while preserving source traceability, auditability, and role-based workflows.

## What this repository includes

- Next.js + TypeScript + Tailwind frontend
- FastAPI + SQLAlchemy backend
- PostgreSQL-ready persistence model
- Violence calculation engine with configurable thresholds
- Sliding Scale Assessment Generator
- Source verification and citation model
- Assessment audit trail and export-ready data structures
- Sample seeded dataset for Afghanistan, Sudan, and Syria examples
- Expanded country catalog covering African states except South Africa, plus requested Middle East countries and Ukraine
- Dockerized local development setup
- Unit tests for the core analytical logic

## Product scope in this MVP

The MVP supports:

- country, region, district, and custom-area assessments
- configurable indicator periods: 1, 3, 6, 12 months and custom dates
- incidents per 100,000 inhabitants
- fatalities per 100,000 inhabitants
- civilian harm indicators
- increasing / stable / decreasing trend labels
- sliding-scale legal reasoning draft generation
- source traceability with URLs, publication dates, and access dates
- live ACLED and UCDP ingestion endpoints wired for real credentials
- officer-entered ACLED / UCDP credentials on the Source Verification page
- help menu and troubleshooting page
- role model scaffolding for Protection Officer, Senior Officer, and Administrator

## Architecture

```text
frontend/   Next.js UI
backend/    FastAPI API, services, models, tests
docs/       API and deployment documentation
```

## Quick start

1. Copy environment template:

```bash
cp .env.example .env
```

2. Run the full stack:

```bash
docker compose up --build
```

3. Open:

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

## Seeded accounts for local development only

The repository includes seeded development accounts to make local MVP testing possible.

- `admin@example.org`
- `senior.officer@example.org`
- `officer@example.org`

Default local development password:

- `ChangeMe123!`

These values are for local development only. Do not use them in any real deployment. Replace all seeded credentials and create real user accounts before any live use.

## Operational scope note

The geography catalog has been expanded for asylum casework coverage, but seeded subnational sample data remains intentionally limited to the MVP example countries already included in the repository. Countries without seeded regions or districts can still be assessed at country level and can receive live ACLED or UCDP ingestion when valid credentials are supplied at runtime.

## Live data integration note

The ACLED and UCDP code paths are implemented and callable. Live fetching requires valid operator credentials:

- ACLED username and password
- UCDP access token

These may be supplied through environment configuration or entered by authorized users in the Source Verification page for a sync run.

## Manual backend run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload
```

## Manual frontend run

```bash
cd frontend
npm install
npm run dev
```

## Production hardening checklist

Before going live:

- replace the default `SECRET_KEY`
- rotate all seeded passwords
- remove or disable demo-style seeded accounts
- create named officer, senior officer, and administrator accounts
- set production `CORS_ORIGINS`
- configure PostgreSQL instead of local SQLite fallback
- store ACLED and UCDP credentials in deployment secrets if you do not want officers to enter them manually
- review audit, retention, and access policies for casework data
- verify deployment health, login, assessment generation, source sync, and export flows in the target environment

## Data model summary

The backend stores:

- countries
- regions
- districts
- violence incidents
- population snapshots
- source references
- risk thresholds
- assessments
- applicant circumstances
- generated narratives
- users and roles

## Important compliance note

This application is an analytical support tool. It does **not** replace the legal assessment of a protection officer.

## Source handling rules implemented in the app

- never fabricate sources
- always show source metadata for displayed indicator inputs
- flag missing data and low-confidence assessments
- separate factual data from generated analytical text

## Key API endpoints

- `POST /api/auth/login`
- `GET /api/geographies/tree`
- `GET /api/incidents/summary`
- `GET /api/thresholds`
- `PUT /api/thresholds/{id}`
- `POST /api/assessments/generate`
- `GET /api/assessments`
- `GET /api/sources/verification`
- `POST /api/source-sync/run`

See `docs/API.md`, `docs/DEPLOYMENT.md`, and `docs/GITHUB_RELEASE_CHECKLIST.md` for details.
