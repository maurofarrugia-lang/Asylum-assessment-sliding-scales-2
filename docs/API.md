# API Documentation

## Authentication

### POST `/api/auth/login`
Returns a bearer token.

Request:
```json
{
  "email": "admin@example.org",
  "password": "ChangeMe123!"
}
```

## Geographies

### GET `/api/geographies/tree`
Returns countries with nested regions and districts.

### GET `/api/geographies/search?q=sudan`
Searches across country, region, and district names.

## Incidents and analytics

### GET `/api/incidents/summary`
Query parameters:
- `geo_type`: `country|region|district|custom`
- `geo_id`: database id for non-custom areas
- `months`: `1|3|6|12`
- `start_date`, `end_date`: optional ISO dates for custom range

Response includes:
- incident_count
- fatalities_total
- civilian_harm_total
- population
- incidents_per_100k
- fatalities_per_100k
- civilian_harm_per_100k
- trend
- confidence
- sources
- data_quality_notes

## Thresholds

### GET `/api/thresholds`
Returns editable risk thresholds.

### PUT `/api/thresholds/{id}`
Administrator-only threshold update.

## Assessments

### POST `/api/assessments/generate`
Creates an assessment and generates a sliding-scale narrative.

Request body:
```json
{
  "officer_name": "Jane Doe",
  "geo_type": "district",
  "geo_id": 7,
  "period_months": 6,
  "applicant": {
    "age": 17,
    "gender": "female",
    "medical_vulnerabilities": "asthma",
    "ethnicity": "Masalit",
    "previous_harm": "family home burned",
    "support_network": "limited",
    "custom_notes": "travelling alone"
  },
  "country_information": {
    "coi_findings": "Recent reports note widespread insecurity and humanitarian constraints.",
    "security_dynamics": "Frequent shelling and checkpoints.",
    "internal_relocation": "Relocation appears difficult due to displacement and insecurity."
  }
}
```

### GET `/api/assessments`
Lists saved assessments with generated text and traceability metadata.

## Sources

### GET `/api/sources/verification`
Shows every source record and the incidents/population records linked to it.

### POST `/api/source-sync/run`
Runs a manual live-ingestion job for ACLED or UCDP.

Request body:
```json
{
  "provider": "acled",
  "geo_type": "country",
  "geo_id": 1,
  "start_date": "2026-01-01",
  "end_date": "2026-05-14"
}
```

Notes:
- ACLED requires `ACLED_USERNAME` and `ACLED_PASSWORD`
- UCDP requires `UCDP_ACCESS_TOKEN`
- UCDP country sync currently uses a country-code mapping table for seeded countries
