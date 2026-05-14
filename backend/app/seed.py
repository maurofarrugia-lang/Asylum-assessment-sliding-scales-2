from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.core.config import get_settings
from app.data.country_catalog import COUNTRY_CATALOG
from app.data.sample_seed import SAMPLE_DATA
from app.models import Country, District, GeoTypeEnum, Incident, PopulationRecord, Region, RiskThreshold, RoleEnum, SourceReference, User

settings = get_settings()


def _get_or_create_source(db: Session, item: dict) -> SourceReference:
    source = db.execute(
        select(SourceReference).where(
            SourceReference.name == item["name"],
            SourceReference.dataset_name == item["dataset_name"],
            SourceReference.reporting_period_start == date.fromisoformat(item["reporting_period_start"]),
            SourceReference.reporting_period_end == date.fromisoformat(item["reporting_period_end"]),
        )
    ).scalars().first()
    if source:
        return source

    source = SourceReference(
        name=item["name"],
        dataset_name=item["dataset_name"],
        url=item["url"],
        publication_date=date.fromisoformat(item["publication_date"]),
        accessed_at=date.fromisoformat(item["accessed_at"]),
        reporting_period_start=date.fromisoformat(item["reporting_period_start"]),
        reporting_period_end=date.fromisoformat(item["reporting_period_end"]),
        reliability_note=item["reliability_note"],
    )
    db.add(source)
    db.flush()
    return source


def _ensure_population_record(db: Session, *, geo_type: GeoTypeEnum, source_id: int, value: int, country_id: int | None = None, region_id: int | None = None, district_id: int | None = None) -> None:
    existing = db.execute(
        select(PopulationRecord).where(
            PopulationRecord.geo_type == geo_type,
            PopulationRecord.country_id == country_id,
            PopulationRecord.region_id == region_id,
            PopulationRecord.district_id == district_id,
        )
    ).scalars().first()
    if existing:
        return
    db.add(
        PopulationRecord(
            geo_type=geo_type,
            country_id=country_id,
            region_id=region_id,
            district_id=district_id,
            value=value,
            as_of_date=date(2025, 12, 31),
            source_id=source_id,
        )
    )


def seed_database(db: Session) -> None:
    sources = [_get_or_create_source(db, item) for item in SAMPLE_DATA["sources"]]
    population_source = next(source for source in sources if source.name == "World Bank")
    incident_source = next(source for source in sources if source.name == "ACLED")
    sample_lookup = {country["name"]: country for country in SAMPLE_DATA["countries"]}

    for country_payload in COUNTRY_CATALOG:
        country = db.execute(select(Country).where(Country.name == country_payload["name"])).scalars().first()
        if not country:
            country = Country(name=country_payload["name"], iso_code=country_payload["iso_code"])
            db.add(country)
            db.flush()

        sample_country = sample_lookup.get(country.name)
        if not sample_country:
            continue

        country_population = sum(d["population_estimate"] for r in sample_country["regions"] for d in r["districts"])
        _ensure_population_record(
            db,
            geo_type=GeoTypeEnum.country,
            country_id=country.id,
            source_id=population_source.id,
            value=country_population,
        )

        for region_payload in sample_country["regions"]:
            region = db.execute(
                select(Region).where(Region.country_id == country.id, Region.name == region_payload["name"])
            ).scalars().first()
            if not region:
                region = Region(name=region_payload["name"], country_id=country.id)
                db.add(region)
                db.flush()

            region_population = sum(d["population_estimate"] for d in region_payload["districts"])
            _ensure_population_record(
                db,
                geo_type=GeoTypeEnum.region,
                region_id=region.id,
                source_id=population_source.id,
                value=region_population,
            )

            for district_payload in region_payload["districts"]:
                district = db.execute(
                    select(District).where(District.region_id == region.id, District.name == district_payload["name"])
                ).scalars().first()
                if not district:
                    district = District(
                        name=district_payload["name"],
                        region_id=region.id,
                        population_estimate=district_payload["population_estimate"],
                    )
                    db.add(district)
                    db.flush()

                _ensure_population_record(
                    db,
                    geo_type=GeoTypeEnum.district,
                    district_id=district.id,
                    source_id=population_source.id,
                    value=district.population_estimate,
                )

                has_seeded_incidents = db.execute(
                    select(Incident).where(Incident.district_id == district.id, Incident.source_id == incident_source.id)
                ).scalars().first()
                if has_seeded_incidents:
                    continue

                for offset in range(1, 7):
                    incident_date = date.today() - timedelta(days=offset * 25)
                    severity = 2 if country.name == "Sudan" and district.name in {"El Fasher", "Khartoum"} else 1
                    db.add(
                        Incident(
                            geo_type=GeoTypeEnum.district,
                            country_id=country.id,
                            region_id=region.id,
                            district_id=district.id,
                            incident_date=incident_date,
                            incident_type="Armed clash" if offset % 2 else "Shelling",
                            fatalities=severity * offset,
                            civilian_harm=max(0, severity * (offset - 1)),
                            description=f"Seeded incident {offset} for {district.name}",
                            source_id=incident_source.id,
                        )
                    )

    thresholds = [
        ("low indiscriminate violence", 0.0, 0.0, "Available data indicates isolated or limited incidents.", 1),
        ("moderate indiscriminate violence", 10.0, 2.0, "Available data indicates recurring incidents and localized civilian exposure.", 2),
        ("high indiscriminate violence", 25.0, 5.0, "Available data indicates frequent incidents with broad civilian exposure.", 3),
        ("exceptional / article 15(c) warning", 50.0, 10.0, "Available data may approach an exceptional level of indiscriminate violence requiring close legal scrutiny.", 4),
    ]
    for label, incidents, fatalities, warning, order in thresholds:
        threshold = db.execute(select(RiskThreshold).where(RiskThreshold.label == label)).scalars().first()
        if threshold:
            continue
        db.add(RiskThreshold(label=label, min_incidents_per_100k=incidents, min_fatalities_per_100k=fatalities, warning_text=warning, sort_order=order))

    users = [
        (settings.default_admin_email, "Default Administrator", RoleEnum.administrator),
        ("senior.officer@example.org", "Senior Protection Officer", RoleEnum.senior_officer),
        ("officer@example.org", "Protection Officer", RoleEnum.protection_officer),
    ]
    for email, full_name, role in users:
        existing_user = db.execute(select(User).where(User.email == email)).scalars().first()
        if existing_user:
            continue
        db.add(
            User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(settings.default_admin_password),
                role=role,
            )
        )

    db.commit()
