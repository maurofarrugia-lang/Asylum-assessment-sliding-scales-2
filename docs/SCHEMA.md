# Database Schema Overview

## Core reference tables

### `users`
- id
- email
- full_name
- hashed_password
- role (`protection_officer`, `senior_officer`, `administrator`)
- is_active
- created_at

### `countries`
- id
- name
- iso_code

### `regions`
- id
- country_id → countries.id
- name

### `districts`
- id
- region_id → regions.id
- name
- population_estimate

## Evidence and calculation tables

### `source_references`
- id
- name
- dataset_name
- url
- publication_date
- accessed_at
- reporting_period_start
- reporting_period_end
- reliability_note

### `population_records`
- id
- geo_type (`country`, `region`, `district`, `custom`)
- country_id / region_id / district_id
- value
- as_of_date
- source_id → source_references.id

### `incidents`
- id
- geo_type (`country`, `region`, `district`, `custom`)
- country_id / region_id / district_id
- incident_date
- incident_type
- fatalities
- civilian_harm
- description
- source_id → source_references.id

## Risk and assessment tables

### `risk_thresholds`
- id
- label
- min_incidents_per_100k
- min_fatalities_per_100k
- warning_text
- sort_order

### `assessments`
- id
- officer_name
- generated_by_user_id → users.id
- geo_type
- country_id / region_id / district_id
- custom_area_name
- period_months
- start_date
- end_date
- indicator_snapshot (JSON)
- applicant_circumstances (JSON)
- country_information (JSON)
- generated_narrative
- source_ids (JSON array)
- confidence
- created_at

## Relationship summary

- One country has many regions.
- One region has many districts.
- One source can support many incident and population rows.
- One user can generate many assessments.
- One assessment stores a point-in-time analytical snapshot for auditability.
