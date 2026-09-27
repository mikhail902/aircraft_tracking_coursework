"""Клиент Nominatim OpenStreetMap."""

from dataclasses import dataclass
from typing import Optional

import requests


@dataclass(frozen=True)
class CountryBounds:
    """Представляет географические границы страны."""

    name: str
    south: float
    north: float
    west: float
    east: float


class NominatimClient:
    """Получает географические данные стран через Nominatim API."""

    def __init__(self, url: str, user_agent: str, timeout: int = 20) -> None:
        """Инициализирует HTTP-клиент Nominatim."""
        self.url = url
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def get_country_bounds(self, country: str) -> Optional[CountryBounds]:
        """Возвращает bounding box указанной страны или None."""
        response = self.session.get(
            self.url,
            params={
                "q": country,
                "format": "jsonv2",
                "limit": 1,
                "featuretype": "country",
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        if not data:
            return None

        # Nominatim: [south, north, west, east]
        bbox = [float(value) for value in data[0]["boundingbox"]]
        return CountryBounds(
            name=country,
            south=bbox[0],
            north=bbox[1],
            west=bbox[2],
            east=bbox[3],
        )
