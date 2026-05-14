from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import Session

from app.models import District, GeoTypeEnum, Incident, PopulationRecord, Region, RiskThreshold, SourceReference


@dataclass
class SummaryBundle:
    area_name: str
    geo_type: GeoTypeEnum
    incident_count: int
    fatalities_total: int
    civilian_harm_total: int
    population: int | None
    incidents_per_100k: float | None
    fatalities_per_100k: float | None
    civilian_harm_per_100k: float | None
    trend: str
    risk_label: str
    warning_text: str
    confidence: str
    data_quality_notes: list[str]
    sources: list[SourceReference]
    source_ids: list[int]


def rate_per_100k(count: int, population: int | None) -> float | None:
    if not population or population <= 0:
        return None
    return round((count / population) * 100000, 2)


def detect_trend(previous: int, current: int) -> str:
    if previous <= 0 and current <= 0:
        return "stable"
    if previous == 0 and current > 0:
        return "increasing"
    change_ratio = (current - previous) / max(previous, 1)
    if change_ratio > 0.15:
        return "increasing"
    if change_ratio < -0.15:
        return "decreasing"
    return "stable"


def classify_risk(incidents_per_100k: float | None, fatalities_per_100k: float | None, thresholds: Iterable[RiskThreshold]) -> tuple[str, str]:
    if incidents_per_100k is None or fatalities_per_100k is None:
        return "insufficient data", "Population or incident coverage is incomplete; legal assessment should proceed with caution."

    selected = None
    for threshold in sorted(thresholds, key=lambda item: item.sort_order):
        if incidents_per_100k >= threshold.min_incidents_per_100k or fatalities_per_100k >= threshold.min_fatalities_per_100k:
            selected = threshold
    if selected is None:
        selected = sorted(thresholds, key=lambda item: item.sort_order)[0]
    return selected.label, selected.warning_text


def _build_geo_filter(geo_type: GeoTypeEnum, geo_id: int | None):
    if geo_type == GeoTypeEnum.country:
        return Incident.country_id == geo_id
    if geo_type == GeoTypeEnum.region:
        return Incident.region_id == geo_id
    if geo_type == GeoTypeEnum.district:
        return Incident.district_id == geo_id
    return None


def _build_population_filter(geo_type: GeoTypeEnum, geo_id: int | None):
    if geo_type == GeoTypeEnum.country:
        return PopulationRecord.country_id == geo_id
    if geo_type == GeoTypeEnum.region:
        return PopulationRecord.region_id == geo_id
    if geo_type == GeoTypeEnum.district:
        return PopulationRecord.district_id == geo_id
    return None


def resolve_area_name(db: Session, geo_type: GeoTypeEnum, geo_id: int | None, custom_area_name: str | None = None) -> str:
    if geo_type == GeoTypeEnum.custom:
        return custom_area_name or "Custom Area"
    if geo_type == GeoTypeEnum.country:
        from app.models import Country
        item = db.get(Country, geo_id)
    elif geo_type == GeoTypeEnum.region:
        item = db.get(Region, geo_id)
    else:
        item = db.get(District, geo_id)
    return item.name if item else "Unknown Area"


def calculate_summary(
    db: Session,
    geo_type: GeoTypeEnum,
    geo_id: int | None,
    months: int,
    start_date: date | None = None,
    end_date: date | None = None,
    custom_area_name: str | None = None,
) -> SummaryBundle:
    end = end_date or date.today()
    start = start_date or (end - timedelta(days=30 * months))
    previous_start = start - timedelta(days=(end - start).days or 30)

    notes: list[str] = []
    area_name = resolve_area_name(db, geo_type, geo_id, custom_area_name)

    if geo_type == GeoTypeEnum.custom:
        notes.append("Custom areas require manual evidence entry or future GIS aggregation; current MVP does not auto-aggregate custom polygons.")
        return SummaryBundle(
            area_name=area_name,
            geo_type=geo_type,
            incident_count=0,
            fatalities_total=0,
            civilian_harm_total=0,
            population=None,
            incidents_per_100k=None,
            fatalities_per_100k=None,
            civilian_harm_per_100k=None,
            trend="stable",
            risk_label="insufficient data",
            warning_text="Custom area auto-calculation is not yet configured.",
            confidence="low",
            data_quality_notes=notes,
            sources=[],
            source_ids=[],
        )

    geo_filter = _build_geo_filter(geo_type, geo_id)
    pop_filter = _build_population_filter(geo_type, geo_id)

    incident_stmt: Select = select(
        func.count(Incident.id),
        func.coalesce(func.sum(Incident.fatalities), 0),
        func.coalesce(func.sum(Incident.civilian_harm), 0),
    ).where(and_(geo_filter, Incident.incident_date >= start, Incident.incident_date <= end))
    incident_count, fatalities_total, civilian_harm_total = db.execute(incident_stmt).one()

    prev_stmt = select(func.count(Incident.id)).where(and_(geo_filter, Incident.incident_date >= previous_start, Incident.incident_date < start))
    previous_incidents = db.execute(prev_stmt).scalar_one()
    trend = detect_trend(previous_incidents, incident_count)

    pop_stmt = (
        select(PopulationRecord)
        .where(and_(pop_filter, PopulationRecord.geo_type == geo_type))
        .order_by(PopulationRecord.as_of_date.desc())
    )
    pop_record = db.execute(pop_stmt).scalars().first()
    population = pop_record.value if pop_record else None
    if population is None:
        notes.append("Population data missing for selected geography.")

    source_ids = set(db.execute(select(Incident.source_id).where(and_(geo_filter, Incident.incident_date >= start, Incident.incident_date <= end))).scalars().all())
    if pop_record:
        source_ids.add(pop_record.source_id)
    sources = db.execute(select(SourceReference).where(SourceReference.id.in_(source_ids))).scalars().all() if source_ids else []

    incidents_per_100k = rate_per_100k(incident_count, population)
    fatalities_per_100k = rate_per_100k(fatalities_total, population)
    civilian_harm_per_100k = rate_per_100k(civilian_harm_total, population)

    thresholds = db.execute(select(RiskThreshold).order_by(RiskThreshold.sort_order)).scalars().all()
    risk_label, warning_text = classify_risk(incidents_per_100k, fatalities_per_100k, thresholds)

    confidence = "high"
    if incident_count < 3 or len(sources) < 2:
        confidence = "medium"
        notes.append("Indicator confidence is moderated by low event volume or limited source diversity.")
    if population is None or not sources:
        confidence = "low"
        notes.append("Assessment confidence is reduced because key reference data is incomplete.")

    return SummaryBundle(
        area_name=area_name,
        geo_type=geo_type,
        incident_count=incident_count,
        fatalities_total=fatalities_total,
        civilian_harm_total=civilian_harm_total,
        population=population,
        incidents_per_100k=incidents_per_100k,
        fatalities_per_100k=fatalities_per_100k,
        civilian_harm_per_100k=civilian_harm_per_100k,
        trend=trend,
        risk_label=risk_label,
        warning_text=warning_text,
        confidence=confidence,
        data_quality_notes=notes,
        sources=sources,
        source_ids=sorted(source_ids),
    )
