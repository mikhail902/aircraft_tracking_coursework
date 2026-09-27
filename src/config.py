"""Конфигурация приложения."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Хранит настройки PostgreSQL, Nominatim и OpenSky."""

    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "aircraft_tracking")
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")

    nominatim_url: str = os.getenv(
        "NOMINATIM_URL",
        "https://nominatim.openstreetmap.org/search",
    )
    nominatim_user_agent: str = os.getenv(
        "NOMINATIM_USER_AGENT",
        "aircraft-tracking-coursework/1.0",
    )

    opensky_api_url: str = os.getenv(
        "OPEN_SKY_API_URL",
        "https://opensky-network.org/api",
    )
    opensky_client_id: str = os.getenv("OPEN_SKY_CLIENT_ID", "")
    opensky_client_secret: str = os.getenv("OPEN_SKY_CLIENT_SECRET", "")
    opensky_token_url: str = os.getenv(
        "OPEN_SKY_TOKEN_URL",
        "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token",
    )


COUNTRIES = (
    "Germany",
    "France",
    "Italy",
    "Spain",
    "Poland",
    "Netherlands",
    "Belgium",
    "Austria",
    "Switzerland",
    "Czechia",
)
