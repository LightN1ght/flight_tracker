from abc import ABC, abstractmethod
from time import monotonic, sleep

import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OPENSKY_URL = "https://opensky-network.org/api/states/all"
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
TIMEOUT = 20


class APIError(RuntimeError):
    """Ошибка запроса или формата ответа внешнего сервиса."""


class AircraftAPI(ABC):
    @abstractmethod
    def get_country_bounds(self, country: str) -> dict[str, float]:
        """Возвращает координаты прямоугольника вокруг страны."""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> list[object]:
        """Возвращает данные о самолётах в заданной области."""


class OpenSkyAircraftAPI(AircraftAPI):
    def __init__(
        self,
        nominatim_url: str = NOMINATIM_URL,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        if bool(client_id) != bool(client_secret):
            raise APIError("Для входа в OpenSky укажите и идентификатор, и секрет клиента.")

        self._nominatim_url = nominatim_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._bounds: dict[str, dict[str, float]] = {}
        self._last_geocoding_request = float("-inf")

    def get_country_bounds(self, country: str) -> dict[str, float]:
        country = country.strip()
        if not country:
            raise APIError("Введите название страны.")

        country_key = country.casefold()
        if country_key in self._bounds:
            return self._bounds[country_key].copy()

        remaining_delay = 1 - (monotonic() - self._last_geocoding_request)
        if remaining_delay > 0:
            sleep(remaining_delay)
        self._last_geocoding_request = monotonic()

        places = self._request_json("Nominatim", "GET", self._nominatim_url,
            params={"country": country, "featureType": "country", "format": "jsonv2", "limit": 1},
            headers={"User-Agent": "LightN1ght-flight-tracker/0.1 (GitHub: LightN1ght/flight_tracker)"},
        )
        if places == []:
            raise APIError(f"Страна «{country}» не найдена.")
        if not isinstance(places, list) or not places or not isinstance(places[0], dict):
            raise APIError("Nominatim вернул некорректный результат поиска.")

        bounds = places[0].get("boundingbox")
        if not isinstance(bounds, list) or len(bounds) != 4:
            raise APIError("Nominatim не вернул четыре координаты страны.")

        try:
            south, north, west, east = map(float, bounds)
        except (TypeError, ValueError, OverflowError) as error:
            raise APIError("Nominatim вернул некорректные координаты страны.") from error

        if not (-90 <= south < north <= 90 and -180 <= west < east <= 180):
            raise APIError("Nominatim вернул координаты за пределами допустимого диапазона.")

        coordinates = {"lamin": south, "lamax": north, "lomin": west, "lomax": east}
        self._bounds[country_key] = coordinates
        return coordinates.copy()

    def get_aeroplanes(self, country: str) -> list[object]:
        coordinates = self.get_country_bounds(country)
        data = self._request_json(
            "OpenSky", "GET", OPENSKY_URL, params=coordinates, headers=self._get_opensky_headers()
        )
        if not isinstance(data, dict) or "states" not in data:
            raise APIError("В ответе OpenSky отсутствует поле states.")

        states = data["states"]
        if states is None:
            return []
        if not isinstance(states, list):
            raise APIError("OpenSky вернул поле states в неверном формате.")
        return states

    def _get_opensky_headers(self) -> dict[str, str]:
        if not self._client_id:
            return {}

        data = self._request_json(
            "OpenSky", "POST", TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        token = data.get("access_token") if isinstance(data, dict) else None
        if not isinstance(token, str) or not token.strip():
            raise APIError("OpenSky не вернул токен доступа.")
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _request_json(service: str, method: str, url: str, **kwargs: object) -> object:
        try:
            response = requests.request(method, url, timeout=TIMEOUT, **kwargs)
            response.raise_for_status()
        except requests.Timeout as error:
            raise APIError(f"{service} не ответил вовремя.") from error
        except requests.HTTPError as error:
            status = error.response.status_code if error.response is not None else None
            if status == 429:
                raise APIError(f"Превышен лимит запросов к {service}. Попробуйте позже.") from error
            if status in (401, 403):
                raise APIError(f"{service} отклонил запрос (HTTP {status}). Проверьте доступ к API.") from error
            raise APIError(f"Ошибка HTTP при запросе к {service} ({status}).") from error
        except requests.RequestException as error:
            raise APIError(f"Не удалось подключиться к {service}.") from error

        try:
            return response.json()
        except ValueError as error:
            raise APIError(f"{service} вернул некорректный JSON.") from error
