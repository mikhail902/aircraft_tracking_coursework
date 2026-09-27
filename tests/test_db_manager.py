"""Тесты SQL-методов DBManager с mock-подключением."""

from unittest.mock import MagicMock, patch

from src.db import DBManager


def make_manager():
    """Возвращает DBManager с тестовыми параметрами."""
    return DBManager("localhost", 5432, "test_db", "postgres", "postgres")


@patch("src.db.psycopg2.connect")
def test_get_avg_speed(mock_connect):
    """Проверяет извлечение среднего значения скорости."""
    connection = MagicMock()
    cursor = MagicMock()
    cursor.fetchone.return_value = (215.5,)
    connection.cursor.return_value.__enter__.return_value = cursor
    mock_connect.return_value.__enter__.return_value = connection

    result = make_manager().get_avg_speed()

    assert result == 215.5
    cursor.execute.assert_called_once()


@patch("src.db.psycopg2.connect")
def test_get_countries_and_count(mock_connect):
    """Проверяет метод подсчёта самолётов по странам."""
    connection = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ("Germany", 12),
        ("France", 8),
    ]
    connection.cursor.return_value.__enter__.return_value = cursor
    mock_connect.return_value.__enter__.return_value = connection

    result = make_manager().get_countries_and_aeroplanes_count()

    assert result == [("Germany", 12), ("France", 8)]
    assert "LEFT JOIN" in cursor.execute.call_args.args[0]


@patch("src.db.psycopg2.connect")
def test_keyword_is_parameterized(mock_connect):
    """Проверяет поиск по callsign с параметризованным запросом."""
    connection = MagicMock()
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    connection.cursor.return_value.__enter__.return_value = cursor
    mock_connect.return_value.__enter__.return_value = connection

    make_manager().get_aeroplanes_with_keyword("ACA")

    args = cursor.execute.call_args.args
    assert "%ACA%" in args[1]
