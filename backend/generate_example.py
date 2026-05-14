from app.db import Base, SessionLocal, engine
from app.seed import seed_database
from app.models import GeoTypeEnum
from app.services.violence import calculate_summary
from app.services.narrative import build_assessment_narrative

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    seed_database(db)
    summary = calculate_summary(db, GeoTypeEnum.district, 1, 6)
    applicant = {
        "age": 17,
        "gender": "female",
        "medical_vulnerabilities": "asthma",
        "ethnicity": "Masalit",
        "family_composition": "single adult with younger sibling",
        "single_status": "single woman",
        "minority_profile": "ethnic minority",
        "occupation": "student",
        "previous_harm": "family home burned",
        "internal_displacement_history": "multiple displacements",
        "support_network": "limited",
        "area_specific_vulnerabilities": "camp insecurity",
        "travel_route_concerns": "unsafe checkpoints",
        "custom_notes": "traveling without stable male support",
    }
    country_info = {
        "coi_findings": "Recent reports describe active hostilities and high humanitarian need.",
        "security_dynamics": "Shelling, checkpoints, and fluid front lines affect civilian movement.",
        "recent_developments": "Recent escalation has reduced predictability and access to services.",
        "localised_risk_patterns": "Urban centers and displacement sites remain exposed.",
        "humanitarian_conditions": "Healthcare and shelter access are constrained.",
        "state_protection": "State protection appears limited in practice.",
        "internal_relocation": "Internal relocation may be unreasonable where displacement and insecurity persist.",
    }
    narrative = build_assessment_narrative(summary, applicant, country_info)
    print(narrative)
finally:
    db.close()
