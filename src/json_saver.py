import json
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.aeroplane import Aeroplane
from src.base_saver import AeroplaneStorage, StorageError

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "aeroplanes.json"


class JSONSaver(AeroplaneStorage):
    def __init__(self, path: str | Path = DEFAULT_PATH) -> None:
        self._path = Path(path)

    def _read_file(self) -> list[Aeroplane]:
        try:
            with self._path.open(encoding="utf-8") as file:
                data = json.load(file)
        except FileNotFoundError:
            return []
        except (OSError, ValueError) as error:
            raise StorageError(f"Не удалось прочитать файл {self._path}.") from error

        if not isinstance(data, list):
            raise StorageError(f"В файле {self._path} должен быть список самолётов.")
        try:
            return [Aeroplane(**item) for item in data]
        except (ValueError, TypeError) as error:
            raise StorageError(f"В файле {self._path} есть некорректные данные о самолётах.") from error

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        self.save_snapshot([*self._read_file(), aeroplane])

    def get_aeroplanes(self, origin_country: str | None = None) -> list[Aeroplane]:
        aeroplanes = self._read_file()
        if origin_country is None:
            return aeroplanes

        country = origin_country.strip().casefold()
        if not country:
            raise ValueError("Введите страну регистрации.")
        return [aeroplane for aeroplane in aeroplanes if aeroplane.origin_country.casefold() == country]

    def delete_aeroplane(self, icao24: str) -> bool:
        aeroplanes = self._read_file()
        icao24 = icao24.strip().lower()
        remaining = [aeroplane for aeroplane in aeroplanes if aeroplane.icao24 != icao24]
        if len(remaining) == len(aeroplanes):
            return False
        self.save_snapshot(remaining)
        return True

    def save_snapshot(self, aeroplanes: Sequence[Aeroplane]) -> None:
        records = {aeroplane.icao24: aeroplane.to_dict() for aeroplane in aeroplanes}
        temporary_path = None
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self._path.parent, delete=False) as file:
                temporary_path = Path(file.name)
                json.dump(list(records.values()), file, ensure_ascii=False, indent=4)
                file.write("\n")
            temporary_path.replace(self._path)
        except OSError as error:
            raise StorageError(f"Не удалось записать данные в файл {self._path}.") from error
        finally:
            if temporary_path is not None:
                with suppress(OSError):
                    temporary_path.unlink(missing_ok=True)
