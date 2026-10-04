"""Клиент OpenSky Network REST API."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import requests


MIN_STATE_LEN = 17

IDX_ICAO24 = 0
IDX_CALLSIGN = 1
IDX_ORIGIN_COUNTRY = 2
IDX_TIME_POSITION = 3
IDX_LAST_CONTACT = 4
IDX_LONGITUDE = 5
IDX_LATITUDE = 6
IDX_BARO_ALTITUDE = 7
IDX_ON_GROUND = 8
IDX_VELOCITY = 9
IDX_TRUE_TRACK = 10
IDX_VERTICAL_RATE = 11
IDX_SENSORS = 12
IDX_GEO_ALTITUDE = 13
IDX_SQUAWK = 14
IDX_SPI = 15
IDX_POSITION_SOURCE = 16
IDX_CATEGORY = 17


@dataclass
class AircraftState:
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
    category: Optional[int] = None


class OpenSkyClient:

    def __init__(
        self,
        api_url: str,
        client_id: str = "",
        client_secret: str = "",
        token_url: str = "",
        timeout: int = 30,
    ) -> None:
        self.api_url = api_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.timeout = timeout
        self.session = requests.Session()
        self._token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def _get_token(self) -> Optional[str]:
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
        token = self._get_token()
        return {"Authorization": f"Bearer {token}"} if token else {}

    @staticmethod
    def _parse_state(state: list) -> Optional[AircraftState]:
        if not state or len(state) < MIN_STATE_LEN:
            return None

        icao24_raw = state[IDX_ICAO24]
        icao24 = (icao24_raw or "").strip().lower()
        if not icao24:
            return None

        callsign_raw = state[IDX_CALLSIGN]
        callsign = (
            callsign_raw.strip() or None
            if isinstance(callsign_raw, str)
            else None
        )

        category = (
            state[IDX_CATEGORY]
            if len(state) > IDX_CATEGORY
            else None
        )

        return AircraftState(
            icao24=icao24,
            callsign=callsign,
            origin_country=state[IDX_ORIGIN_COUNTRY],
            time_position=state[IDX_TIME_POSITION],
            last_contact=state[IDX_LAST_CONTACT],
            longitude=state[IDX_LONGITUDE],
            latitude=state[IDX_LATITUDE],
            baro_altitude=state[IDX_BARO_ALTITUDE],
            on_ground=state[IDX_ON_GROUND],
            velocity=state[IDX_VELOCITY],
            true_track=state[IDX_TRUE_TRACK],
            vertical_rate=state[IDX_VERTICAL_RATE],
            geo_altitude=state[IDX_GEO_ALTITUDE],
            squawk=state[IDX_SQUAWK],
            category=category,
        )

    def get_states(
        self,
        south: float,
        west: float,
        north: float,
        east: float,
    ) -> List[AircraftState]:
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
            parsed = self._parse_state(state)
            if parsed is not None:
                result.append(parsed)

        return result