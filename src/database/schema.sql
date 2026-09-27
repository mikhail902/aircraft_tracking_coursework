CREATE TABLE IF NOT EXISTS countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    south DOUBLE PRECISION NOT NULL,
    north DOUBLE PRECISION NOT NULL,
    west DOUBLE PRECISION NOT NULL,
    east DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS aircraft (
    icao24 VARCHAR(6) PRIMARY KEY,
    country_id INTEGER NOT NULL REFERENCES countries(id) ON DELETE CASCADE,
    callsign VARCHAR(8),
    origin_country VARCHAR(100),
    time_position BIGINT,
    last_contact BIGINT,
    longitude DOUBLE PRECISION,
    latitude DOUBLE PRECISION,
    baro_altitude DOUBLE PRECISION,
    on_ground BOOLEAN,
    velocity DOUBLE PRECISION,
    true_track DOUBLE PRECISION,
    vertical_rate DOUBLE PRECISION,
    geo_altitude DOUBLE PRECISION,
    squawk VARCHAR(4),
    category INTEGER,
    observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_aircraft_country_id
    ON aircraft(country_id);

CREATE INDEX IF NOT EXISTS idx_aircraft_callsign
    ON aircraft(callsign);

CREATE INDEX IF NOT EXISTS idx_aircraft_velocity
    ON aircraft(velocity);
