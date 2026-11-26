from abc import ABC, abstractmethod
from collections.abc import Sequence

from src.aeroplane import Aeroplane


class StorageError(RuntimeError):
    """Ошибка чтения или записи хранилища."""


class AeroplaneStorage(ABC):
    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет или обновляет самолёт по адресу ICAO."""

    @abstractmethod
    def get_aeroplanes(self, origin_country: str | None = None) -> list[Aeroplane]:
        """Возвращает все записи или только самолёты из указанной страны."""

    @abstractmethod
    def delete_aeroplane(self, icao24: str) -> bool:
        """Удаляет самолёт по адресу ICAO и сообщает, была ли найдена запись."""

    @abstractmethod
    def save_snapshot(self, aeroplanes: Sequence[Aeroplane]) -> None:
        """Заменяет записи результатом текущей загрузки."""
