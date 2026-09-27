"""Сервис сбора и сохранения данных."""

from typing import Iterable

from src.api.nominatim import NominatimClient
from src.api.opensky import OpenSkyClient
from src.db import DBManager


class AircraftCollector:
    """Оркестрирует получение данных из API и запись в PostgreSQL."""

    def __init__(
        self,
        nominatim: NominatimClient,
        opensky: OpenSkyClient,
        db: DBManager,
    ) -> None:
        """Создаёт сервис с тремя необходимыми зависимостями."""
        self.nominatim = nominatim
        self.opensky = opensky
        self.db = db

    def collect(self, countries: Iterable[str]) -> None:
        """Получает страны и воздушные суда и сохраняет их в БД."""
        for country in countries:
            bounds = self.nominatim.get_country_bounds(country)
            if bounds is None:
                print(f"[WARN] Не найдены координаты: {country}")
                continue

            country_id = self.db.upsert_country(
                bounds.name,
                bounds.south,
                bounds.north,
                bounds.west,
                bounds.east,
            )

            try:
                aircraft = self.opensky.get_states(
                    bounds.south,
                    bounds.west,
                    bounds.north,
                    bounds.east,
                )
                self.db.save_aircraft_batch(country_id, aircraft)
                print(f"[OK] {country}: получено {len(aircraft)} воздушных судов")
            except Exception as exc:
                # Ошибка одной страны не прерывает весь сбор.
                print(f"[WARN] {country}: {exc}")
