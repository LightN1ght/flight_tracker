from unittest.mock import Mock

import pytest
import requests

from src.api import NOMINATIM_URL, OPENSKY_URL, TOKEN_URL, AircraftAPI, APIError, OpenSkyAircraftAPI


@pytest.fixture
def search_result():
    return [{"boundingbox": ["45.8", "47.8", "5.9", "10.5"]}]


def mock_response(data):
    response = Mock(spec=requests.Response)
    response.json.return_value = data
    return response


def test_aircraft_api_is_abstract():
    with pytest.raises(TypeError):
        AircraftAPI()  # type: ignore[abstract]


def test_get_aeroplanes(monkeypatch, search_result):
    states = [["a1b2c3", "TEST1", "France"]]
    request = Mock(side_effect=[mock_response(search_result), mock_response({"states": states})])
    monkeypatch.setattr("src.api.requests.request", request)

    assert OpenSkyAircraftAPI().get_aeroplanes(" Switzerland ") == states

    first, second = request.call_args_list
    assert first.args == ("GET", NOMINATIM_URL)
    assert first.kwargs["params"] == {
        "country": "Switzerland",
        "featureType": "country",
        "format": "jsonv2",
        "limit": 1,
    }
    assert "flight-tracker" in first.kwargs["headers"]["User-Agent"]
    assert second.args == ("GET", OPENSKY_URL)
    assert second.kwargs["params"] == {"lamin": 45.8, "lamax": 47.8, "lomin": 5.9, "lomax": 10.5}
    assert second.kwargs["timeout"] > 0


def test_country_bounds_are_cached(monkeypatch, search_result):
    request = Mock(return_value=mock_response(search_result))
    monkeypatch.setattr("src.api.requests.request", request)

    api = OpenSkyAircraftAPI()
    first = api.get_country_bounds("Switzerland")
    first["lamin"] = 0
    assert api.get_country_bounds(" switzerland ")["lamin"] == 45.8
    request.assert_called_once()


def test_country_lookup_waits_between_requests(monkeypatch, search_result):
    request = Mock(return_value=mock_response(search_result))
    wait = Mock()
    monkeypatch.setattr("src.api.requests.request", request)
    monkeypatch.setattr("src.api.monotonic", Mock(side_effect=[10, 10, 10.25, 11]))
    monkeypatch.setattr("src.api.sleep", wait)

    api = OpenSkyAircraftAPI()
    api.get_country_bounds("Spain")
    api.get_country_bounds("France")
    wait.assert_called_once_with(0.75)


@pytest.mark.parametrize(
    "country, response, message",
    [
        (" ", [], "Введите название страны"),
        ("Unknown", [], "не найдена"),
        ("Spain", ["Spain"], "некорректный результат"),
        ("Spain", [{}], "четыре координаты"),
        ("Spain", [{"boundingbox": ["bad", "50", "-10", "15"]}], "некорректные координаты"),
        ("Spain", [{"boundingbox": ["110", "120", "-10", "15"]}], "допустимого диапазона"),
    ],
)
def test_invalid_country_bounds(monkeypatch, country, response, message):
    monkeypatch.setattr("src.api.requests.request", Mock(return_value=mock_response(response)))

    with pytest.raises(APIError, match=message):
        OpenSkyAircraftAPI().get_country_bounds(country)


@pytest.mark.parametrize("states", [None, []])
def test_empty_states(monkeypatch, search_result, states):
    request = Mock(side_effect=[mock_response(search_result), mock_response({"states": states})])
    monkeypatch.setattr("src.api.requests.request", request)

    assert OpenSkyAircraftAPI().get_aeroplanes("Spain") == []


@pytest.mark.parametrize("data", [{}, {"states": "invalid"}])
def test_invalid_states(monkeypatch, search_result, data):
    request = Mock(side_effect=[mock_response(search_result), mock_response(data)])
    monkeypatch.setattr("src.api.requests.request", request)

    with pytest.raises(APIError, match="states"):
        OpenSkyAircraftAPI().get_aeroplanes("Spain")


@pytest.mark.parametrize(
    "error, message", [(requests.Timeout, "не ответил вовремя"), (requests.ConnectionError, "подключиться")]
)
def test_connection_errors(monkeypatch, error, message):
    monkeypatch.setattr("src.api.requests.request", Mock(side_effect=error))

    with pytest.raises(APIError, match=message):
        OpenSkyAircraftAPI().get_country_bounds("Spain")


@pytest.mark.parametrize("status, message", [(429, "лимит"), (403, "отклонил"), (503, "Ошибка HTTP")])
def test_http_errors(monkeypatch, status, message):
    response = requests.Response()
    response.status_code = status
    response.url = NOMINATIM_URL
    monkeypatch.setattr("src.api.requests.request", Mock(return_value=response))

    with pytest.raises(APIError, match=message):
        OpenSkyAircraftAPI().get_country_bounds("Spain")


def test_invalid_json(monkeypatch):
    response = mock_response(None)
    response.json.side_effect = ValueError
    monkeypatch.setattr("src.api.requests.request", Mock(return_value=response))

    with pytest.raises(APIError, match="некорректный JSON"):
        OpenSkyAircraftAPI().get_country_bounds("Spain")


def test_opensky_authentication(monkeypatch, search_result):
    request = Mock(
        side_effect=[
            mock_response(search_result),
            mock_response({"access_token": "example"}),
            mock_response({"states": []}),
        ]
    )
    monkeypatch.setattr("src.api.requests.request", request)

    OpenSkyAircraftAPI(client_id="example", client_secret="example").get_aeroplanes("Spain")

    _, token, states = request.call_args_list
    assert token.args == ("POST", TOKEN_URL)
    assert token.kwargs["data"]["grant_type"] == "client_credentials"
    assert states.kwargs["headers"] == {"Authorization": "Bearer example"}


def test_incomplete_credentials():
    with pytest.raises(APIError, match="секрет"):
        OpenSkyAircraftAPI(client_id="example")


def test_missing_token(monkeypatch, search_result):
    request = Mock(side_effect=[mock_response(search_result), mock_response({})])
    monkeypatch.setattr("src.api.requests.request", request)

    with pytest.raises(APIError, match="токен"):
        OpenSkyAircraftAPI(client_id="example", client_secret="example").get_aeroplanes("Spain")
