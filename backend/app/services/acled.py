from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()


class AcledConfigurationError(RuntimeError):
    pass


@dataclass
class AcledEvent:
    event_date: date
    event_type: str
    fatalities: int
    civilian_harm: int
    country: str
    admin1: str | None
    admin2: str | None
    description: str | None
    raw: dict[str, Any]


class AcledClient:
    def __init__(self, username: str | None = None, password: str | None = None) -> None:
        self.base_url = settings.acled_api_url
        self.token_url = settings.acled_token_url
        self.username = username or settings.acled_username
        self.password = password or settings.acled_password
        self._access_token: str | None = None
        self._token_expiry: datetime | None = None

    def configured(self) -> bool:
        return bool(self.username and self.password)

    def _ensure_token(self) -> str:
        if not self.configured():
            raise AcledConfigurationError("ACLED credentials are not configured. Enter them in the app or set them in the environment.")
        if self._access_token and self._token_expiry and datetime.utcnow() < self._token_expiry:
            return self._access_token

        response = httpx.post(
            self.token_url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "username": self.username,
                "password": self.password,
                "grant_type": "password",
                "client_id": "acled",
                "scope": "authenticated",
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        self._access_token = payload["access_token"]
        self._token_expiry = datetime.utcnow() + timedelta(seconds=int(payload.get("expires_in", 86400)) - 60)
        return self._access_token

    def fetch_events(
        self,
        *,
        country: str,
        start_date: date,
        end_date: date,
        admin1: str | None = None,
        admin2: str | None = None,
        limit: int = 5000,
        max_pages: int = 20,
    ) -> tuple[list[AcledEvent], dict[str, Any]]:
        token = self._ensure_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        params: dict[str, Any] = {
            "country": country,
            "event_date": f"{start_date.isoformat()}|{end_date.isoformat()}",
            "event_date_where": "BETWEEN",
            "limit": limit,
            "page": 1,
            "with_total": "true",
            "fields": "event_date|event_type|sub_event_type|country|admin1|admin2|location|notes|fatalities|civilian_targeting|disorder_type|source|source_scale|timestamp",
            "_format": "json",
        }
        if admin1:
            params["admin1"] = admin1
            params["admin1_where"] = "LIKE"
        if admin2:
            params["admin2"] = admin2
            params["admin2_where"] = "LIKE"

        events: list[AcledEvent] = []
        total_count: int | None = None
        pages_fetched = 0
        while pages_fetched < max_pages:
            response = httpx.get(self.base_url, headers=headers, params=params, timeout=60)
            response.raise_for_status()
            payload = response.json()
            rows = payload.get("data") or []
            total_count = payload.get("total_count", total_count)
            for row in rows:
                civilian_harm = 1 if row.get("civilian_targeting") else 0
                description = row.get("notes") or row.get("sub_event_type")
                events.append(
                    AcledEvent(
                        event_date=date.fromisoformat(row["event_date"]),
                        event_type=row.get("event_type") or row.get("sub_event_type") or "Conflict event",
                        fatalities=int(row.get("fatalities") or 0),
                        civilian_harm=civilian_harm,
                        country=row.get("country") or country,
                        admin1=row.get("admin1"),
                        admin2=row.get("admin2"),
                        description=description,
                        raw=row,
                    )
                )
            pages_fetched += 1
            if len(rows) < limit:
                break
            params["page"] += 1

        metadata = {
            "provider": "ACLED",
            "total_count": total_count if total_count is not None else len(events),
            "pages_fetched": pages_fetched,
            "reporting_period_start": start_date.isoformat(),
            "reporting_period_end": end_date.isoformat(),
            "url": self.base_url,
        }
        return events, metadata
