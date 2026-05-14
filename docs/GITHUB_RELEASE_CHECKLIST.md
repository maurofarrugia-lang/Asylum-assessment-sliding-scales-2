# GitHub Push-Ready Branch / Release Checklist

## Branch preparation

- Create a feature branch, for example: `feat/live-ingestion-help-menu`
- Confirm `.env` is excluded from version control
- Keep `.env.example` updated with every required variable
- Remove generated local artifacts before commit (`.venv`, `.next`, `node_modules`, local SQLite database)

## Verification before push

### Backend
- `cd backend`
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `pytest`

### Frontend
- `cd frontend`
- `npm install`
- `npm run lint`
- `npm run build`

### Smoke tests
- Backend health responds on `/health`
- Login works with seeded admin account
- Dashboard loads even if live source credentials are missing
- Source Verification page renders configured integration states
- Help menu opens and routes correctly
- Assessment generation saves a case

## Pull request checklist

- Explain whether ACLED and UCDP live credentials were tested or only wired structurally
- Include screenshots of Dashboard, Sliding Scale Generator, Source Verification, and Help
- Note any manual setup steps for operators
- Link relevant issue / ticket

## Release checklist

- Merge PR
- Create release tag (e.g. `v0.2.0`)
- Publish release notes summarizing:
  - live ACLED/UCDP wiring
  - help menu and troubleshooting page
  - source sync endpoints
  - any credential prerequisites
