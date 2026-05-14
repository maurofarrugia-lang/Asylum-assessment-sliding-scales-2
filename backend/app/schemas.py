from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import GeoTypeEnum, RoleEnum


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: RoleEnum


class SourceReferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    dataset_name: str
    url: str
    publication_date: date | None
    accessed_at: date
    reporting_period_start: date | None
    reporting_period_end: date | None
    reliability_note: str | None


class DistrictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    population_estimate: int | None


class RegionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    districts: list[DistrictOut]


class CountryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    iso_code: str
    regions: list[RegionOut]


class ThresholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    label: str
    min_incidents_per_100k: float
    min_fatalities_per_100k: float
    warning_text: str
    sort_order: int


class ThresholdUpdate(BaseModel):
    min_incidents_per_100k: float
    min_fatalities_per_100k: float
    warning_text: str


class ApplicantCircumstances(BaseModel):
    age: int | None = None
    gender: str | None = None
    disability: str | None = None
    medical_vulnerabilities: str | None = None
    ethnicity: str | None = None
    religion: str | None = None
    family_composition: str | None = None
    single_status: str | None = None
    child_status: str | None = None
    minority_profile: str | None = None
    political_visibility: str | None = None
    occupation: str | None = None
    previous_harm: str | None = None
    internal_displacement_history: str | None = None
    support_network: str | None = None
    area_specific_vulnerabilities: str | None = None
    travel_route_concerns: str | None = None
    custom_notes: str | None = None


class CountryInformationInput(BaseModel):
    coi_findings: str | None = None
    security_dynamics: str | None = None
    recent_developments: str | None = None
    localised_risk_patterns: str | None = None
    humanitarian_conditions: str | None = None
    state_protection: str | None = None
    internal_relocation: str | None = None


class ProviderCredentialsInput(BaseModel):
    acled_username: str | None = None
    acled_password: str | None = None
    ucdp_access_token: str | None = None
    ucdp_country_code_override: int | None = None


class SyncRequest(BaseModel):
    provider: Literal["acled", "ucdp"]
    geo_type: GeoTypeEnum
    geo_id: int | None = None
    start_date: date
    end_date: date
    credentials: ProviderCredentialsInput = Field(default_factory=ProviderCredentialsInput)


class AssessmentGenerateRequest(BaseModel):
    officer_name: str
    geo_type: GeoTypeEnum
    geo_id: int | None = None
    custom_area_name: str | None = None
    period_months: Literal[1, 3, 6, 12] = 6
    start_date: date | None = None
    end_date: date | None = None
    applicant: ApplicantCircumstances = Field(default_factory=ApplicantCircumstances)
    country_information: CountryInformationInput = Field(default_factory=CountryInformationInput)


class SummaryResponse(BaseModel):
    geo_type: GeoTypeEnum
    area_name: str
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
    sources: list[SourceReferenceOut]


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    officer_name: str
    geo_type: GeoTypeEnum
    period_months: int
    generated_narrative: str
    confidence: str
    indicator_snapshot: dict[str, Any]
    applicant_circumstances: dict[str, Any]
    country_information: dict[str, Any]
    source_ids: list[int]
    created_at: datetime
