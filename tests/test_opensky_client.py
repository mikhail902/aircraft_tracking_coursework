from src.api.opensky import OpenSkyClient


def test_parse_full_state_with_category():
    state = [
        "ABC123", "AFL123 ", "Russia",
        1700000000, 1700000001,
        37.5, 55.7,
        10000.0, False,
        250.0, 90.0, 1.5,
        None, 10200.0, "1234",
        False, 0,
        3,
    ]
    parsed = OpenSkyClient._parse_state(state)
    assert parsed is not None
    assert parsed.icao24 == "abc123"
    assert parsed.callsign == "AFL123"
    assert parsed.category == 3


def test_parse_state_without_category():
    state = [
        "ABC123", "AFL123", "Russia",
        1700000000, 1700000001,
        37.5, 55.7,
        10000.0, False,
        250.0, 90.0, 1.5,
        None, 10200.0, "1234",
        False, 0,
    ]
    parsed = OpenSkyClient._parse_state(state)
    assert parsed is not None
    assert parsed.category is None


def test_parse_short_state_returns_none():
    assert OpenSkyClient._parse_state([1, 2, 3]) is None
    assert OpenSkyClient._parse_state([]) is None
    assert OpenSkyClient._parse_state(None) is None


def test_parse_empty_icao_returns_none():
    state = [None] + list(range(1, 18))
    assert OpenSkyClient._parse_state(state) is None


def test_parse_none_callsign():
    state = [
        "ABC123", None, "Russia",
        1700000000, 1700000001,
        37.5, 55.7,
        10000.0, False,
        250.0, 90.0, 1.5,
        None, 10200.0, "1234",
        False, 0,
    ]
    parsed = OpenSkyClient._parse_state(state)
    assert parsed is not None
    assert parsed.callsign is None