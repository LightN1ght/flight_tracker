import math
import re
from collections.abc import Sequence


class Aeroplane:
    def __init__(
        self,
        icao24: str,
        callsign: str | None,
        origin_country: str,
        velocity: float | None,
        baro_altitude: float | None,
        on_ground: bool,
    ) -> None:
        if not isinstance(icao24, str) or re.fullmatch(r"[0-9a-fA-F]{6}", icao24.strip()) is None:
            raise ValueError("Адрес ICAO должен содержать 6 шестнадцатеричных символов.")
        if callsign is not None and not isinstance(callsign, str):
            raise ValueError("Позывной должен быть строкой.")
        if not isinstance(origin_country, str) or not origin_country.strip():
            raise ValueError("Укажите страну регистрации.")
        if not isinstance(on_ground, bool):
            raise ValueError("Признак нахождения на земле должен быть логическим значением.")

        self.__icao24 = icao24.strip().lower()
        self.__callsign = (callsign.strip() or None) if callsign is not None else None
        self.__origin_country = origin_country.strip()
        self.__velocity = self._validate_number(velocity, "Скорость")
        self.__baro_altitude = self._validate_number(baro_altitude, "Высота")
        self.__on_ground = on_ground
        if self.__velocity is not None and self.__velocity < 0:
            raise ValueError("Скорость не может быть отрицательной.")

    @staticmethod
    def _validate_number(value: float | None, name: str) -> float | None:
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} должна быть числом.")
        try:
            number = float(value)
        except OverflowError as error:
            raise ValueError(f"{name} должна быть конечным числом.") from error
        if not math.isfinite(number):
            raise ValueError(f"{name} должна быть конечным числом.")
        return number

    @property
    def icao24(self) -> str:
        return self.__icao24

    @property
    def callsign(self) -> str | None:
        return self.__callsign

    @property
    def origin_country(self) -> str:
        return self.__origin_country

    @property
    def velocity(self) -> float | None:
        return self.__velocity

    @property
    def baro_altitude(self) -> float | None:
        return self.__baro_altitude

    @property
    def on_ground(self) -> bool:
        return self.__on_ground

    def compare_by_speed(self, other: "Aeroplane") -> int | None:
        """Сравнивает самолёты по скорости, если есть оба значения."""
        if self.velocity is None or other.velocity is None:
            return None
        return (self.velocity > other.velocity) - (self.velocity < other.velocity)

    def compare_by_altitude(self, other: "Aeroplane") -> int | None:
        """Сравнивает самолёты по высоте, если есть оба значения."""
        if self.baro_altitude is None or other.baro_altitude is None:
            return None
        return (self.baro_altitude > other.baro_altitude) - (self.baro_altitude < other.baro_altitude)

    @classmethod
    def cast_to_object_list(cls, states: Sequence[object]) -> list["Aeroplane"]:
        """Создаёт самолёты из строк OpenSky и пропускает повреждённые строки."""
        aeroplanes = []
        for state in states:
            if not isinstance(state, list) or len(state) < 10:
                continue
            try:
                aeroplanes.append(cls(state[0], state[1], state[2], state[9], state[7], state[8]))
            except ValueError:
                continue

        if states and not aeroplanes:
            raise ValueError("OpenSky не вернул ни одной корректной записи о самолёте.")
        return aeroplanes

    def to_dict(self) -> dict[str, str | float | bool | None]:
        """Возвращает данные самолёта для сохранения в JSON."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "baro_altitude": self.baro_altitude,
            "on_ground": self.on_ground,
        }

    def __str__(self) -> str:
        callsign = self.callsign or "нет позывного"
        altitude = f"{self.baro_altitude:.1f} м" if self.baro_altitude is not None else "нет данных"
        speed = f"{self.velocity:.1f} м/с" if self.velocity is not None else "нет данных"
        status = "на земле" if self.on_ground else "в воздухе"
        return f"{callsign} ({self.icao24}) | {self.origin_country} | Высота: {altitude} | Скорость: {speed} | {status}"
