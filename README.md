# Курсовая работа: мониторинг воздушных судов

Проект получает координаты выбранных стран через Nominatim OpenStreetMap, затем получает текущие state vectors воздушных судов из OpenSky Network и сохраняет данные в PostgreSQL.

## Структура

```text
aircraft_tracking_coursework/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── nominatim.py
│   │   └── opensky.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── schema.sql
│   ├── services/
│   │   ├── __init__.py
│   │   └── collector.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_db_manager.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Что реализовано

- минимум 10 стран для мониторинга;
- получение географических координат стран через Nominatim;
- получение текущих воздушных судов через OpenSky `/states/all`;
- PostgreSQL;
- `psycopg2`;
- отдельный класс `DBManager`;
- все 5 требуемых методов;
- параметризованные SQL-запросы;
- UPSERT для повторного запуска;
- обработка отсутствующих значений API;
- `.env` для секретов и настроек;
- тесты SQL-логики с mock;
- документация классов и методов.

## Страны

По умолчанию используются:

1. Germany
2. France
3. Italy
4. Spain
5. Poland
6. Netherlands
7. Belgium
8. Austria
9. Switzerland
10. Czechia

При запуске координаты не захардкожены: они запрашиваются у Nominatim.

## Требования

- Python 3.11+
- PostgreSQL 14+
- интернет-соединение
- при использовании актуальной авторизации OpenSky — `OPEN_SKY_CLIENT_ID` и `OPEN_SKY_CLIENT_SECRET`

## Установка

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

Создайте БД PostgreSQL, например:

```sql
CREATE DATABASE aircraft_tracking;
```

Скопируйте `.env.example` в `.env` и заполните параметры подключения.

## Запуск

```bash
python -m src.main
```

Программа:

1. создаёт таблицы;
2. получает координаты стран;
3. сохраняет страны;
4. запрашивает самолёты в bounding box каждой страны;
5. сохраняет воздушные суда;
6. выводит результаты методов `DBManager`.

### Важно про OpenSky

OpenSky сейчас использует OAuth2 Client Credentials для аутентифицированного API-доступа. В проекте предусмотрена автоматическая работа с Bearer token. Если API-доступ без авторизации доступен для вашего аккаунта/лимита, можно оставить OAuth-поля пустыми.

Один запрос `/states/all` с bounding box используется для каждой страны. Это соответствует документации OpenSky и позволяет ограничить область запроса.

## SQL

Схема находится в `src/database/schema.sql`.

Таблицы:

- `countries` — страны и bounding box;
- `aircraft` — последние полученные состояния воздушных судов.

Связь:

```text
countries 1 ──────── N aircraft
```

Поле `country_id` связывает воздушное судно со страной, в чьём bounding box оно было найдено.

## Методы DBManager

### `get_countries_and_aeroplanes_count()`

Возвращает все страны и количество воздушных судов, используя `LEFT JOIN`, поэтому страны без самолётов также присутствуют в результате.

### `get_all_aeroplanes()`

Возвращает все сохранённые воздушные суда вместе с названием страны.

### `get_avg_speed()`

Считает среднюю скорость по всем воздушным судам с известной скоростью.

### `get_aeroplanes_with_higher_speed()`

Возвращает самолёты, скорость которых выше средней.

### `get_aeroplanes_with_keyword(keyword)`

Ищет самолёты по подстроке в callsign без учёта регистра.

Например:

```python
db.get_aeroplanes_with_keyword("ACA")
```

## Проверка

```bash
pytest -q
```

## Примечание по координатам

Nominatim возвращает bounding box страны. OpenSky `/states/all` также принимает bounding box. Поэтому в учебном проекте воздушные суда связываются со страной по попаданию текущих координат в полученный bounding box.

Это именно учебная геопространственная аппроксимация, а не юридическая граница воздушного пространства. Пограничные зоны могут пересекаться между bounding box соседних стран.
