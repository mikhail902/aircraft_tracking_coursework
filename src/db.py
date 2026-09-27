"""Работа с PostgreSQL и класс DBManager."""

from pathlib import Path
from typing import Any, List, Optional, Tuple

import psycopg2
from psycopg2.extras import execute_values


class DBManager:
    """Предоставляет методы для работы с таблицами курсового проекта."""

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> None:
        """Сохраняет параметры подключения к PostgreSQL."""
        self.connection_params = {
            "host": host,
            "port": port,
            "dbname": database,
            "user": user,
            "password": password,
        }

    def _connect(self):
        """Создаёт новое подключение к PostgreSQL."""
        return psycopg2.connect(**self.connection_params)

    def create_tables(self, schema_path: Optional[str] = None) -> None:
        """Создаёт таблицы countries и aircraft из SQL-схемы."""
        path = Path(schema_path or Path(__file__).parent / "database" / "schema.sql")
        sql = path.read_text(encoding="utf-8")
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)

    def upsert_country(
        self,
        name: str,
        south: float,
        north: float,
        west: float,
        east: float,
    ) -> int:
        """Добавляет страну или обновляет её bounding box."""
        query = """
            INSERT INTO countries (name, south, north, west, east)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                south = EXCLUDED.south,
                north = EXCLUDED.north,
                west = EXCLUDED.west,
                east = EXCLUDED.east
            RETURNING id;
        """
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (name, south, north, west, east))
                return cursor.fetchone()[0]

    def save_aircraft(self, country_id: int, aircraft: Any) -> None:
        """Сохраняет или обновляет состояние воздушного судна."""
        query = """
            INSERT INTO aircraft (
                icao24, country_id, callsign, origin_country,
                time_position, last_contact, longitude, latitude,
                baro_altitude, on_ground, velocity, true_track,
                vertical_rate, geo_altitude, squawk, category,
                observed_at
            )
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, NOW()
            )
            ON CONFLICT (icao24) DO UPDATE SET
                country_id = EXCLUDED.country_id,
                callsign = EXCLUDED.callsign,
                origin_country = EXCLUDED.origin_country,
                time_position = EXCLUDED.time_position,
                last_contact = EXCLUDED.last_contact,
                longitude = EXCLUDED.longitude,
                latitude = EXCLUDED.latitude,
                baro_altitude = EXCLUDED.baro_altitude,
                on_ground = EXCLUDED.on_ground,
                velocity = EXCLUDED.velocity,
                true_track = EXCLUDED.true_track,
                vertical_rate = EXCLUDED.vertical_rate,
                geo_altitude = EXCLUDED.geo_altitude,
                squawk = EXCLUDED.squawk,
                category = EXCLUDED.category,
                observed_at = NOW();
        """
        values = (
            aircraft.icao24,
            country_id,
            aircraft.callsign,
            aircraft.origin_country,
            aircraft.time_position,
            aircraft.last_contact,
            aircraft.longitude,
            aircraft.latitude,
            aircraft.baro_altitude,
            aircraft.on_ground,
            aircraft.velocity,
            aircraft.true_track,
            aircraft.vertical_rate,
            aircraft.geo_altitude,
            aircraft.squawk,
            aircraft.category,
        )
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, values)

    def save_aircraft_batch(self, country_id: int, aircraft_list: list) -> None:
        """Пакетно сохраняет несколько воздушных судов."""
        if not aircraft_list:
            return

        query = """
            INSERT INTO aircraft (
                icao24, country_id, callsign, origin_country,
                time_position, last_contact, longitude, latitude,
                baro_altitude, on_ground, velocity, true_track,
                vertical_rate, geo_altitude, squawk, category,
                observed_at
            ) VALUES %s
            ON CONFLICT (icao24) DO UPDATE SET
                country_id = EXCLUDED.country_id,
                callsign = EXCLUDED.callsign,
                origin_country = EXCLUDED.origin_country,
                time_position = EXCLUDED.time_position,
                last_contact = EXCLUDED.last_contact,
                longitude = EXCLUDED.longitude,
                latitude = EXCLUDED.latitude,
                baro_altitude = EXCLUDED.baro_altitude,
                on_ground = EXCLUDED.on_ground,
                velocity = EXCLUDED.velocity,
                true_track = EXCLUDED.true_track,
                vertical_rate = EXCLUDED.vertical_rate,
                geo_altitude = EXCLUDED.geo_altitude,
                squawk = EXCLUDED.squawk,
                category = EXCLUDED.category,
                observed_at = NOW();
        """

        values = [
            (
                a.icao24, country_id, a.callsign, a.origin_country,
                a.time_position, a.last_contact, a.longitude, a.latitude,
                a.baro_altitude, a.on_ground, a.velocity, a.true_track,
                a.vertical_rate, a.geo_altitude, a.squawk, a.category,
                # PostgreSQL принимает NOW() в запросе, значение здесь
                # оставлено как None только для соответствия форме.
                None,
            )
            for a in aircraft_list
        ]

        # Для observed_at используем отдельный вариант без поля.
        query = """
            INSERT INTO aircraft (
                icao24, country_id, callsign, origin_country,
                time_position, last_contact, longitude, latitude,
                baro_altitude, on_ground, velocity, true_track,
                vertical_rate, geo_altitude, squawk, category
            ) VALUES %s
            ON CONFLICT (icao24) DO UPDATE SET
                country_id = EXCLUDED.country_id,
                callsign = EXCLUDED.callsign,
                origin_country = EXCLUDED.origin_country,
                time_position = EXCLUDED.time_position,
                last_contact = EXCLUDED.last_contact,
                longitude = EXCLUDED.longitude,
                latitude = EXCLUDED.latitude,
                baro_altitude = EXCLUDED.baro_altitude,
                on_ground = EXCLUDED.on_ground,
                velocity = EXCLUDED.velocity,
                true_track = EXCLUDED.true_track,
                vertical_rate = EXCLUDED.vertical_rate,
                geo_altitude = EXCLUDED.geo_altitude,
                squawk = EXCLUDED.squawk,
                category = EXCLUDED.category,
                observed_at = NOW();
        """
        values = [
            (
                a.icao24, country_id, a.callsign, a.origin_country,
                a.time_position, a.last_contact, a.longitude, a.latitude,
                a.baro_altitude, a.on_ground, a.velocity, a.true_track,
                a.vertical_rate, a.geo_altitude, a.squawk, a.category,
            )
            for a in aircraft_list
        ]

        with self._connect() as connection:
            with connection.cursor() as cursor:
                execute_values(cursor, query, values)

    def get_countries_and_aeroplanes_count(self) -> List[Tuple]:
        """Возвращает все страны и число самолётов в их воздушных пространствах."""
        query = """
            SELECT c.name, COUNT(a.icao24) AS aeroplanes_count
            FROM countries AS c
            LEFT JOIN aircraft AS a ON a.country_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.name;
        """
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_all_aeroplanes(self) -> List[Tuple]:
        """Возвращает список всех воздушных судов и их основные данные."""
        query = """
            SELECT
                a.icao24,
                a.callsign,
                a.origin_country,
                c.name AS monitored_country,
                a.longitude,
                a.latitude,
                a.baro_altitude,
                a.velocity,
                a.true_track,
                a.vertical_rate,
                a.geo_altitude,
                a.squawk,
                a.category,
                a.observed_at
            FROM aircraft AS a
            JOIN countries AS c ON c.id = a.country_id
            ORDER BY a.icao24;
        """
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_avg_speed(self) -> Optional[float]:
        """Возвращает среднюю скорость воздушных судов в м/с."""
        query = "SELECT AVG(velocity) FROM aircraft WHERE velocity IS NOT NULL;"
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()[0]
                return float(result) if result is not None else None

    def get_aeroplanes_with_higher_speed(self) -> List[Tuple]:
        """Возвращает воздушные суда со скоростью выше средней."""
        query = """
            SELECT
                a.icao24,
                a.callsign,
                a.velocity,
                c.name AS monitored_country
            FROM aircraft AS a
            JOIN countries AS c ON c.id = a.country_id
            WHERE a.velocity > (
                SELECT AVG(velocity)
                FROM aircraft
                WHERE velocity IS NOT NULL
            )
            ORDER BY a.velocity DESC;
        """
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Tuple]:
        """Возвращает самолёты, в callsign которых содержится keyword."""
        query = """
            SELECT
                a.icao24,
                a.callsign,
                a.origin_country,
                c.name AS monitored_country,
                a.velocity
            FROM aircraft AS a
            JOIN countries AS c ON c.id = a.country_id
            WHERE a.callsign ILIKE %s
            ORDER BY a.callsign, a.icao24;
        """
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (f"%{keyword}%",))
                return cursor.fetchall()
