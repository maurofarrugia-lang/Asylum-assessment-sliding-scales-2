from datetime import date, datetime
from enum import Enum

from sqlalchemy import JSON, Boolean, Date, DateTime, Enum as SqlEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class RoleEnum(str, Enum):
    protection_officer = "protection_officer"
    senior_officer = "senior_officer"
    administrator = "administrator"


class GeoTypeEnum(str, Enum):
    country = "country"
    region = "region"
    district = "district"
    custom = "custom"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[RoleEnum] = mapped_column(SqlEnum(RoleEnum), default=RoleEnum.protection_officer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Country(Base):
    __tablename__ = "countries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    iso_code: Mapped[str] = mapped_column(String(3), unique=True)
    regions: Mapped[list["Region"]] = relationship(back_populates="country", cascade="all, delete-orphan")


class Region(Base):
    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"))
    name: Mapped[str] = mapped_column(String(255))
    country: Mapped[Country] = relationship(back_populates="regions")
    districts: Mapped[list["District"]] = relationship(back_populates="region", cascade="all, delete-orphan")


class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"))
    name: Mapped[str] = mapped_column(String(255))
    population_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    region: Mapped[Region] = relationship(back_populates="districts")


class SourceReference(Base):
    __tablename__ = "source_references"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    dataset_name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    accessed_at: Mapped[date] = mapped_column(Date)
    reporting_period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    reporting_period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    reliability_note: Mapped[str | None] = mapped_column(Text, nullable=True)


class PopulationRecord(Base):
    __tablename__ = "population_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geo_type: Mapped[GeoTypeEnum] = mapped_column(SqlEnum(GeoTypeEnum))
    country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    value: Mapped[int] = mapped_column(Integer)
    as_of_date: Mapped[date] = mapped_column(Date)
    source_id: Mapped[int] = mapped_column(ForeignKey("source_references.id"))


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geo_type: Mapped[GeoTypeEnum] = mapped_column(SqlEnum(GeoTypeEnum))
    country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    incident_date: Mapped[date] = mapped_column(Date)
    incident_type: Mapped[str] = mapped_column(String(255))
    fatalities: Mapped[int] = mapped_column(Integer, default=0)
    civilian_harm: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("source_references.id"))


class RiskThreshold(Base):
    __tablename__ = "risk_thresholds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    label: Mapped[str] = mapped_column(String(100), unique=True)
    min_incidents_per_100k: Mapped[float] = mapped_column(Float)
    min_fatalities_per_100k: Mapped[float] = mapped_column(Float)
    warning_text: Mapped[str] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    officer_name: Mapped[str] = mapped_column(String(255))
    generated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    geo_type: Mapped[GeoTypeEnum] = mapped_column(SqlEnum(GeoTypeEnum))
    country_id: Mapped[int | None] = mapped_column(ForeignKey("countries.id"), nullable=True)
    region_id: Mapped[int | None] = mapped_column(ForeignKey("regions.id"), nullable=True)
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"), nullable=True)
    custom_area_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    period_months: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    indicator_snapshot: Mapped[dict] = mapped_column(JSON)
    applicant_circumstances: Mapped[dict] = mapped_column(JSON)
    country_information: Mapped[dict] = mapped_column(JSON)
    generated_narrative: Mapped[str] = mapped_column(Text)
    source_ids: Mapped[list[int]] = mapped_column(JSON)
    confidence: Mapped[str] = mapped_column(String(50), default="medium")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
