"""Точка входа в курсовой проект."""

from src.api.nominatim import NominatimClient
from src.api.opensky import OpenSkyClient
from src.config import COUNTRIES, Settings
from src.db import DBManager
from src.services.collector import AircraftCollector


def main() -> None:
    """Запускает сбор данных и демонстрирует методы DBManager."""
    settings = Settings()

    db = DBManager(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
    db.create_tables()

    nominatim = NominatimClient(
        url=settings.nominatim_url,
        user_agent=settings.nominatim_user_agent,
    )
    opensky = OpenSkyClient(
        api_url=settings.opensky_api_url,
        client_id=settings.opensky_client_id,
        client_secret=settings.opensky_client_secret,
        token_url=settings.opensky_token_url,
    )

    collector = AircraftCollector(nominatim, opensky, db)
    collector.collect(COUNTRIES)

    print("\n=== Страны и количество самолётов ===")
    for row in db.get_countries_and_aeroplanes_count():
        print(row)

    print("\n=== Средняя скорость ===")
    print(db.get_avg_speed(), "м/с")

    print("\n=== Самолёты быстрее средней скорости ===")
    for row in db.get_aeroplanes_with_higher_speed():
        print(row)

    print("\n=== Поиск по keyword='ACA' ===")
    for row in db.get_aeroplanes_with_keyword("ACA"):
        print(row)

    print("\n=== Общее количество воздушных судов ===")
    print(len(db.get_all_aeroplanes()))


if __name__ == "__main__":
    main()
