# Deployment Guide

## Deployment targets

This repository is prepared for:
- Docker
- Railway
- Azure App Service / Azure Container Apps
- Vercel for the frontend

## Recommended production topology

- Frontend on Vercel
- Backend on Railway or Azure Container Apps
- PostgreSQL managed instance on Railway, Azure Database for PostgreSQL, or Neon

## Backend environment variables

Set all values from `.env.example`, especially:
- `DATABASE_URL`
- `SECRET_KEY`
- `CORS_ORIGINS`
- `DEFAULT_ADMIN_EMAIL`
- `DEFAULT_ADMIN_PASSWORD`
- `ACLED_USERNAME`
- `ACLED_PASSWORD`
- `UCDP_ACCESS_TOKEN`

## Railway

1. Provision PostgreSQL.
2. Deploy `backend/` as a service.
3. Set `DATABASE_URL` to the provisioned database connection string.
4. Deploy `frontend/` or connect it to Vercel.
5. Point `NEXT_PUBLIC_API_BASE_URL` to the backend public URL.

## Azure

1. Build and publish Docker images for frontend and backend.
2. Create Azure Database for PostgreSQL.
3. Inject secrets through Application Settings or Key Vault.
4. Ensure backend CORS allows the frontend hostname.

## Vercel

Frontend can be deployed directly from `frontend/`.
Set:
- `NEXT_PUBLIC_API_BASE_URL`

## GitHub Actions

A sample CI workflow runs backend tests and frontend linting on push.
