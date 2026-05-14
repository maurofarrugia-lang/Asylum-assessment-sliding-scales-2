from app.core.config import get_settings



def configured_source_registry() -> list[dict]:
    settings = get_settings()
    return [
        {
            "name": "ACLED",
            "purpose": "Conflict and incident database",
            "configured": bool(settings.acled_username and settings.acled_password),
            "url": settings.acled_api_url,
            "authentication": "OAuth password grant via Bearer token",
        },
        {
            "name": "UCDP",
            "purpose": "Conflict event dataset",
            "configured": bool(settings.ucdp_access_token),
            "url": settings.ucdp_api_url,
            "authentication": "x-ucdp-access-token header",
        },
        {
            "name": "UNHCR Refworld",
            "purpose": "Country information and legal materials",
            "configured": True,
            "url": settings.refworld_base_url,
            "authentication": "Public web source",
        },
        {
            "name": "ReliefWeb",
            "purpose": "Humanitarian and security developments",
            "configured": True,
            "url": settings.reliefweb_api_url,
            "authentication": "Public API / web source",
        },
    ]
