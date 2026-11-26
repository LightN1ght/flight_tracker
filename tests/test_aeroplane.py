import pytest

from src.aeroplane import Aeroplane


def test_init_aeroplane(aeroplane):
    assert aeroplane.icao24 == "a1b2c3"
    assert aeroplane.callsign == "TEST1"
    assert aeroplane.origin_country == "United Kingdom"
    assert aeroplane.velocity == 240.0
    assert aeroplane.baro_altitude == 9000.0
    assert aeroplane.on_ground is False

    with pytest.raises(AttributeError):
        aeroplane.velocity = -1


def test_compare_aeroplanes(aeroplane):
    other = Aeroplane("a1b2c4", "TEST2", "France", 200, 11000, False)

    assert aeroplane.compare_by_speed(other) == 1
    assert other.compare_by_speed(aeroplane) == -1
    assert aeroplane.compare_by_altitude(other) == -1
    assert other.compare_by_altitude(aeroplane) == 1
    assert aeroplane.compare_by_speed(aeroplane) == 0
    assert aeroplane.compare_by_altitude(aeroplane) == 0


def test_compare_aeroplanes_without_measurements(aeroplane):
    other = Aeroplane("a1b2c4", None, "France", None, None, True)

    assert aeroplane.compare_by_speed(other) is None
    assert other.compare_by_altitude(aeroplane) is None


@pytest.mark.parametrize(
    "field, value",
    [
        ("icao24", "not-a-hex"),
        ("icao24", None),
        ("callsign", 123),
        ("origin_country", ""),
        ("velocity", -1),
        ("velocity", "150"),
        ("velocity", False),
        ("velocity", 10**400),
        ("baro_altitude", float("nan")),
        ("baro_altitude", float("inf")),
        ("on_ground", 0),
    ],
)
def test_invalid_aeroplane_data(aeroplane, field, value):
    data = aeroplane.to_dict()
    data[field] = value

    with pytest.raises(ValueError):
        Aeroplane(**data)


def test_cast_to_object_list():
    result = Aeroplane.cast_to_object_list([
        ["A1B2C3", " ", "Switzerland", None, None, 7, 46, -10, True, 0],
        ["bad", None, "France", None, None, 7, 46, None, True, None],
        "invalid row",
    ])

    assert len(result) == 1
    assert result[0].icao24 == "a1b2c3"
    assert result[0].callsign is None
    assert result[0].baro_altitude == -10
    assert result[0].velocity == 0


def test_cast_empty_list():
    assert Aeroplane.cast_to_object_list([]) == []


def test_cast_invalid_list():
    with pytest.raises(ValueError, match="корректной записи"):
        Aeroplane.cast_to_object_list([["bad"]])


def test_aeroplane_str(aeroplane):
    assert str(aeroplane) == "TEST1 (a1b2c3) | United Kingdom | Высота: 9000.0 м | Скорость: 240.0 м/с | в воздухе"
    other = Aeroplane("a1b2c4", None, "France", None, None, True)
    assert str(other) == "нет позывного (a1b2c4) | France | Высота: нет данных | Скорость: нет данных | на земле"
