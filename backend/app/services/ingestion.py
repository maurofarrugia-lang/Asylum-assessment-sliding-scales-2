from __future__ import annotations

from datetime import date
from typing import Any, Literal

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Country, District, GeoTypeEnum, Incident, Region, SourceReference
from app.services.acled import AcledClient, AcledConfigurationError
from app.services.ucdp import UcdpClient, UcdpConfigurationError

Provider = Literal["acled", "ucdp"]


def _resolve_geo(db: Session, geo_type: GeoTypeEnum, geo_id: int | None) -> tuple[Country | None, Region | None, District | None]:
    country = region = district = None
    if geo_type == GeoTypeEnum.country:
        country = db.get(Country, geo_id)
    elif geo_type == GeoTypeEnum.region:
        region = db.get(Region, geo_id)
        country = db.get(Country, region.country_id) if region else None
    elif geo_type == GeoTypeEnum.district:
        district = db.get(District, geo_id)
        region = db.get(Region, district.region_id) if district else None
        country = db.get(Country, region.country_id) if region else None
    return country, region, district


def _upsert_source(
    db: Session,
    *,
    provider_name: str,
    dataset_name: str,
    url: str,
    start_date: date,
    end_date: date,
    reliability_note: str,
) -> SourceReference:
    existing = db.execute(
        select(SourceReference).where(
            SourceReference.name == provider_name,
            SourceReference.dataset_name == dataset_name,
            SourceReference.reporting_period_start == start_date,
            SourceReference.reporting_period_end == end_date,
        )
    ).scalars().first()
    if existing:
        existing.url = url
        existing.accessed_at = date.today()
        existing.reliability_note = reliability_note
        db.flush()
        return existing

    source = SourceReference(
        name=provider_name,
        dataset_name=dataset_name,
        url=url,
        publication_date=None,
        accessed_at=date.today(),
        reporting_period_start=start_date,
        reporting_period_end=end_date,
        reliability_note=reliability_note,
    )
    db.add(source)
    db.flush()
    return source


def sync_provider(
    db: Session,
    *,
    provider: Provider,
    geo_type: GeoTypeEnum,
    geo_id: int | None,
    start_date: date,
    end_date: date,
    credentials: dict[str, Any] | None = None,
) -> dict:
    country, region, district = _resolve_geo(db, geo_type, geo_id)
    if not country:
        raise ValueError("Selected geography could not be resolved to a country.")

    credentials = credentials or {}
    country_name = country.name
    region_name = region.name if region else None
    district_name = district.name if district else None

    if provider == "acled":
        client = AcledClient(
            username=credentials.get("acled_username") or None,
            password=credentials.get("acled_password") or None,
        )
        if not client.configured():
            raise AcledConfigurationError("ACLED credentials are required. Enter a username and password in the Source Verification page or set them in the environment.")
        events, meta = client.fetch_events(
            country=country_name,
            admin1=region_name,
            admin2=district_name,
            start_date=start_date,
            end_date=end_date,
        )
        source = _upsert_source(
            db,
            provider_name="ACLED",
            dataset_name=f"{country_name} conflict incidents",
            url=meta["url"],
            start_date=start_date,
            end_date=end_date,
            reliability_note="Programmatic ACLED ingestion via OAuth-backed API.",
        )
        provider_label = "ACLED"
    else:
        client = UcdpClient(access_token=credentials.get("ucdp_access_token") or None)
        if not client.configured():
            raise UcdpConfigurationError("UCDP access token is required. Enter it in the Source Verification page or set UCDP_ACCESS_TOKEN in the environment.")
        events, meta = client.fetch_events(
            country=country_name,
            start_date=start_date,
            end_date=end_date,
            country_code_override=credentials.get("ucdp_country_code_override"),
        )
        source = _upsert_source(
            db,
            provider_name="UCDP",
            dataset_name=f"{country_name} GED events",
            url=meta["url"],
            start_date=start_date,
            end_date=end_date,
            reliability_note="Programmatic UCDP GED ingestion via token-authenticated API.",
        )
        provider_label = "UCDP"

    delete_stmt = delete(Incident).where(
        Incident.source_id == source.id,
        Incident.geo_type == geo_type,
    )
    if geo_type == GeoTypeEnum.country:
        delete_stmt = delete_stmt.where(Incident.country_id == country.id)
    elif geo_type == GeoTypeEnum.region and region:
        delete_stmt = delete_stmt.where(Incident.region_id == region.id)
    elif geo_type == GeoTypeEnum.district and district:
        delete_stmt = delete_stmt.where(Incident.district_id == district.id)
    db.execute(delete_stmt)

    inserted = 0
    for event in events:
        region_field = getattr(event, "admin1", None) or getattr(event, "adm_1", None)
        district_field = getattr(event, "admin2", None) or getattr(event, "adm_2", None)
        if geo_type == GeoTypeEnum.region and region_name and region_field and region_name.lower() not in region_field.lower():
            continue
        if geo_type == GeoTypeEnum.district and district_name and (not district_field or district_name.lower() not in district_field.lower()):
            continue
        db.add(
            Incident(
                geo_type=geo_type,
                country_id=country.id if country else None,
                region_id=region.id if region else None,
                district_id=district.id if district else None,
                incident_date=event.event_date,
                incident_type=event.event_type,
                fatalities=event.fatalities,
                civilian_harm=event.civilian_harm,
                description=event.description,
                source_id=source.id,
            )
        )
        inserted += 1

    db.commit()
    return {
        "provider": provider_label,
        "inserted": inserted,
        "source_id": source.id,
        "country": country_name,
        "region": region_name,
        "district": district_name,
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "metadata": meta,
    }
