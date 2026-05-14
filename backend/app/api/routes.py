from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.auth import authenticate_user, create_access_token, get_current_user, require_role
from app.db import get_db
from app.models import Assessment, Country, District, GeoTypeEnum, Region, RiskThreshold, RoleEnum, SourceReference, User
from app.schemas import (
    AssessmentGenerateRequest,
    AssessmentResponse,
    CountryOut,
    LoginRequest,
    SummaryResponse,
    SyncRequest,
    ThresholdOut,
    ThresholdUpdate,
    TokenResponse,
)
from app.services.acled import AcledConfigurationError
from app.services.data_sources import configured_source_registry
from app.services.ingestion import sync_provider
from app.services.narrative import build_assessment_narrative
from app.services.ucdp import UcdpConfigurationError
from app.services.violence import calculate_summary

router = APIRouter(prefix="/api")


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user.email, "role": user.role.value})
    return TokenResponse(access_token=token)


@router.get("/geographies/tree", response_model=list[CountryOut])
def geography_tree(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    countries = db.execute(
        select(Country).options(selectinload(Country.regions).selectinload(Region.districts)).order_by(Country.name)
    ).scalars().all()
    return [
        CountryOut(
            id=country.id,
            name=country.name,
            iso_code=country.iso_code,
            regions=[
                {
                    "id": region.id,
                    "name": region.name,
                    "districts": [
                        {"id": district.id, "name": district.name, "population_estimate": district.population_estimate}
                        for district in region.districts
                    ],
                }
                for region in country.regions
            ],
        )
        for country in countries
    ]


@router.get("/geographies/search")
def geography_search(q: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    countries = db.execute(select(Country).where(Country.name.ilike(f"%{q}%"))).scalars().all()
    regions = db.execute(select(Region).where(Region.name.ilike(f"%{q}%"))).scalars().all()
    districts = db.execute(select(District).where(District.name.ilike(f"%{q}%"))).scalars().all()
    return {
        "countries": [{"id": c.id, "name": c.name} for c in countries],
        "regions": [{"id": r.id, "name": r.name, "country_id": r.country_id} for r in regions],
        "districts": [{"id": d.id, "name": d.name, "region_id": d.region_id} for d in districts],
    }


@router.get("/incidents/summary", response_model=SummaryResponse)
def incidents_summary(
    geo_type: GeoTypeEnum,
    geo_id: int | None = None,
    months: int = Query(default=6, ge=1, le=12),
    start_date: date | None = None,
    end_date: date | None = None,
    custom_area_name: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    summary = calculate_summary(db, geo_type, geo_id, months, start_date, end_date, custom_area_name)
    return SummaryResponse(
        geo_type=summary.geo_type,
        area_name=summary.area_name,
        incident_count=summary.incident_count,
        fatalities_total=summary.fatalities_total,
        civilian_harm_total=summary.civilian_harm_total,
        population=summary.population,
        incidents_per_100k=summary.incidents_per_100k,
        fatalities_per_100k=summary.fatalities_per_100k,
        civilian_harm_per_100k=summary.civilian_harm_per_100k,
        trend=summary.trend,
        risk_label=summary.risk_label,
        warning_text=summary.warning_text,
        confidence=summary.confidence,
        data_quality_notes=summary.data_quality_notes,
        sources=summary.sources,
    )


@router.get("/thresholds", response_model=list[ThresholdOut])
def list_thresholds(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.execute(select(RiskThreshold).order_by(RiskThreshold.sort_order)).scalars().all()


@router.put("/thresholds/{threshold_id}", response_model=ThresholdOut)
def update_threshold(
    threshold_id: int,
    payload: ThresholdUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(RoleEnum.administrator)),
):
    threshold = db.get(RiskThreshold, threshold_id)
    if not threshold:
        raise HTTPException(status_code=404, detail="Threshold not found")
    threshold.min_incidents_per_100k = payload.min_incidents_per_100k
    threshold.min_fatalities_per_100k = payload.min_fatalities_per_100k
    threshold.warning_text = payload.warning_text
    db.commit()
    db.refresh(threshold)
    return threshold


@router.post("/assessments/generate", response_model=AssessmentResponse)
def generate_assessment(
    payload: AssessmentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    summary = calculate_summary(
        db,
        payload.geo_type,
        payload.geo_id,
        payload.period_months,
        payload.start_date,
        payload.end_date,
        payload.custom_area_name,
    )
    narrative = build_assessment_narrative(summary, payload.applicant.model_dump(), payload.country_information.model_dump())

    country_id = region_id = district_id = None
    if payload.geo_type == GeoTypeEnum.country:
        country_id = payload.geo_id
    elif payload.geo_type == GeoTypeEnum.region:
        region_id = payload.geo_id
    elif payload.geo_type == GeoTypeEnum.district:
        district_id = payload.geo_id

    assessment = Assessment(
        officer_name=payload.officer_name,
        generated_by_user_id=current_user.id,
        geo_type=payload.geo_type,
        country_id=country_id,
        region_id=region_id,
        district_id=district_id,
        custom_area_name=payload.custom_area_name,
        period_months=payload.period_months,
        start_date=payload.start_date,
        end_date=payload.end_date,
        indicator_snapshot={
            "area_name": summary.area_name,
            "incident_count": summary.incident_count,
            "fatalities_total": summary.fatalities_total,
            "civilian_harm_total": summary.civilian_harm_total,
            "population": summary.population,
            "incidents_per_100k": summary.incidents_per_100k,
            "fatalities_per_100k": summary.fatalities_per_100k,
            "civilian_harm_per_100k": summary.civilian_harm_per_100k,
            "trend": summary.trend,
            "risk_label": summary.risk_label,
            "warning_text": summary.warning_text,
            "limitations": summary.data_quality_notes,
        },
        applicant_circumstances=payload.applicant.model_dump(),
        country_information=payload.country_information.model_dump(),
        generated_narrative=narrative,
        source_ids=summary.source_ids,
        confidence=summary.confidence,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment


@router.get("/assessments", response_model=list[AssessmentResponse])
def list_assessments(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.execute(select(Assessment).order_by(Assessment.created_at.desc())).scalars().all()


@router.get("/sources/verification")
def source_verification(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    sources = db.execute(select(SourceReference).order_by(SourceReference.name, SourceReference.id.desc())).scalars().all()
    return {
        "configured_integrations": configured_source_registry(),
        "sources": [
            {
                "id": source.id,
                "name": source.name,
                "dataset_name": source.dataset_name,
                "url": source.url,
                "publication_date": source.publication_date,
                "accessed_at": source.accessed_at,
                "reporting_period_start": source.reporting_period_start,
                "reporting_period_end": source.reporting_period_end,
                "reliability_note": source.reliability_note,
            }
            for source in sources
        ],
    }


@router.get("/source-sync/status")
def source_sync_status(_: User = Depends(get_current_user)):
    return {"integrations": configured_source_registry()}


@router.post("/source-sync/run")
def run_source_sync(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(RoleEnum.administrator, RoleEnum.senior_officer)),
):
    try:
        return sync_provider(
            db,
            provider=payload.provider,
            geo_type=payload.geo_type,
            geo_id=payload.geo_id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            credentials=payload.credentials.model_dump(exclude_none=True),
        )
    except (AcledConfigurationError, UcdpConfigurationError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
