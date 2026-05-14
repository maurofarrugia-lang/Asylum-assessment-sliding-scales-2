from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./asylum_app.db"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 120
    default_admin_email: str = "admin@example.org"
    default_admin_password: str = "ChangeMe123!"
    cors_origins: str = "http://localhost:3000"
    acled_api_url: str = "https://acleddata.com/api/acled/read"
    acled_token_url: str = "https://acleddata.com/oauth/token"
    acled_username: str = ""
    acled_password: str = ""
    ucdp_api_url: str = "https://ucdpapi.pcr.uu.se/api/gedevents/25.1"
    ucdp_access_token: str = ""
    refworld_base_url: str = "https://www.refworld.org"
    reliefweb_api_url: str = "https://api.reliefweb.int/v1/reports"

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache

def get_settings() -> Settings:
    return Settings()
