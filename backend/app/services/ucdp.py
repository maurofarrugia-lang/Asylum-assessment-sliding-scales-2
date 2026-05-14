from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()

COUNTRY_CODE_MAP = {
    "Afghanistan": 700,
    "Algeria": 615,
    "Angola": 540,
    "Bahrain": 692,
    "Benin": 434,
    "Botswana": 571,
    "Burkina Faso": 439,
    "Burundi": 516,
    "Cameroon": 471,
    "Central African Republic": 482,
    "Chad": 483,
    "Comoros": 581,
    "Congo": 484,
    "Cote d'Ivoire": 437,
    "Democratic Republic of the Congo": 490,
    "Djibouti": 522,
    "Egypt": 651,
    "Equatorial Guinea": 411,
    "Eritrea": 531,
    "Eswatini": 572,
    "Ethiopia": 530,
    "Gabon": 481,
    "Gambia": 420,
    "Ghana": 452,
    "Guinea": 438,
    "Guinea-Bissau": 404,
    "Iran": 630,
    "Iraq": 645,
    "Israel": 666,
    "Jordan": 663,
    "Kenya": 501,
    "Kuwait": 690,
    "Lebanon": 660,
    "Lesotho": 570,
    "Liberia": 450,
    "Libya": 620,
    "Madagascar": 580,
    "Malawi": 553,
    "Mali": 432,
    "Mauritania": 435,
    "Mauritius": 590,
    "Morocco": 600,
    "Mozambique": 541,
    "Namibia": 565,
    "Niger": 436,
    "Nigeria": 475,
    "Oman": 698,
    "Palestine": 669,
    "Qatar": 694,
    "Rwanda": 517,
    "Saudi Arabia": 670,
    "Senegal": 433,
    "Sierra Leone": 451,
    "Somalia": 520,
    "South Sudan": 626,
    "Sudan": 625,
    "Syria": 652,
    "Tanzania": 510,
    "Togo": 461,
    "Tunisia": 616,
    "Turkey": 640,
    "Uganda": 500,
    "Ukraine": 369,
    "United Arab Emirates": 696,
    "Yemen": 678,
    "Zambia": 551,
    "Zimbabwe": 552,
}


class UcdpConfigurationError(RuntimeError):
    pass


@dataclass
class UcdpEvent:
    event_date: date
    event_type: str
    fatalities: int
    civilian_harm: int
    country: str
    adm_1: str | None
    adm_2: str | None
    description: str | None
    raw: dict[str, Any]


class UcdpClient:
    def __init__(self, access_token: str | None = None) -> None:
        self.base_url = settings.ucdp_api_url
        self.access_token = access_token or settings.ucdp_access_token

    def configured(self) -> bool:
        return bool(self.access_token)

    def _headers(self) -> dict[str, str]:
        if not self.configured():
            raise UcdpConfigurationError("UCDP access token is not configured. Enter it in the app or set it in the environment.")
        return {"x-ucdp-access-token": self.access_token}

    def fetch_events(
        self,
        *,
        country: str,
        start_date: date,
        end_date: date,
        country_code_override: int | None = None,
        pagesize: int = 1000,
        max_pages: int = 20,
    ) -> tuple[list[UcdpEvent], dict[str, Any]]:
        country_code = country_code_override or COUNTRY_CODE_MAP.get(country)
        if not country_code:
            raise UcdpConfigurationError(f"No UCDP country code mapping is configured for {country}. Enter a country code override in the app.")

        page = 0
        total_pages = 1
        total_count = 0
        events: list[UcdpEvent] = []
        while page < total_pages and page < max_pages:
            response = httpx.get(
                self.base_url,
                headers=self._headers(),
                params={
                    "pagesize": pagesize,
                    "page": page,
                    "Country": country_code,
                    "StartDate": start_date.isoformat(),
                    "EndDate": end_date.isoformat(),
                },
                timeout=60,
            )
            response.raise_for_status()
            payload = response.json()
            total_pages = int(payload.get("TotalPages", 1))
            total_count = int(payload.get("TotalCount", 0))
            for row in payload.get("Result", []):
                deaths_civilians = int(row.get("deaths_civilians") or 0)
                events.append(
                    UcdpEvent(
                        event_date=date.fromisoformat(row["date_end"]),
                        event_type=f"UCDP type {row.get('type_of_violence', 'n/a')}",
                        fatalities=int(row.get("best") or 0),
                        civilian_harm=deaths_civilians,
                        country=row.get("country") or country,
                        adm_1=row.get("adm_1"),
                        adm_2=row.get("adm_2"),
                        description=row.get("where_description") or row.get("dyad_name"),
                        raw=row,
                    )
                )
            page += 1

        metadata = {
            "provider": "UCDP",
            "country_code": country_code,
            "total_count": total_count,
            "pages_fetched": page,
            "reporting_period_start": start_date.isoformat(),
            "reporting_period_end": end_date.isoformat(),
            "url": self.base_url,
        }
        return events, metadata
