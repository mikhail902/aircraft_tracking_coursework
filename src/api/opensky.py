"""Клиент OpenSky Network REST API."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests


@dataclass
class AircraftState:
    """Хранит основные поля state vector воздушного судна."""

    icao24: str
    callsign: Optional[str]
    origin_country: Optional[str]
    time_position: Optional[int]
    last_contact: Optional[int]
    longitude: Optional[float]
    latitude: Optional[float]
    baro_altitude: Optional[float]
    on_ground: Optional[bool]
    velocity: Optional[float]
    true_track: Optional[float]
    vertical_rate: Optional[float]
    geo_altitude: Optional[float]
    squawk: Optional[str]
    category: Optional[int]


class OpenSkyClient:
    """Получает текущие state vectors из OpenSky."""

    def __init__(
        self,
        api_url: str,
        client_id: str = "",
        client_secret: str = "",
        token_url: str = "",
        timeout: int = 30,
    ) -> None:
        """Инициализирует OpenSky-клиент и параметры OAuth2."""
        self.api_url = api_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.timeout = timeout
        self.session = requests.Session()
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def _get_token(self) -> Optional[str]:
        """Получает или обновляет OAuth2 access token."""
        if not (self.client_id and self.client_secret and self.token_url):
            return None

        now = datetime.now(timezone.utc)
        if (
            self._token
            and self._token_expires_at
            and now < self._token_expires_at
        ):
            return self._token

        response = self.session.post(
            self.token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        expires_in = int(data.get("expires_in", 1800))
        self._token = data["access_token"]
        self._token_expires_at = now + timedelta(
            seconds=max(0, expires_in - 30)
        )
        return self._token

    def _headers(self) -> dict:
        """Возвращает HTTP-заголовки с актуальным Bearer token."""
        token = self._get_token()
        return {"Authorization": f"Bearer {token}"} if token else {}

    def get_states(
        self,
        south: float,
        west: float,
        north: float,
        east: float,
    ) -> List[AircraftState]:
        """Получает воздушные суда в заданном bounding box."""
        response = self.session.get(
            f"{self.api_url}/states/all",
            params={
                "lamin": south,
                "lomin": west,
                "lamax": north,
                "lomax": east,
            },
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()

        result: List[AircraftState] = []
        for state in payload.get("states") or []:
            # Индексы соответствуют state vector OpenSky.
            result.append(
                AircraftState(
                    icao24=(state[0] or "").lower(),
                    callsign=state[1].strip() if state[1] else None,
                    origin_country=state[2],
                    time_position=state[3],
                    last_contact=state[4],
                    longitude=state[5],
                    latitude=state[6],
                    baro_altitude=state[7],
                    on_ground=state[8],
                    velocity=state[9],
                    true_track=state[10],
                    vertical_rate=state[11],
                    geo_altitude=state[13],
                    squawk=state[14],
                    category=state[17],
                )
            )

        return [item for item in result if item.icao24]
