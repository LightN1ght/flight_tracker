import json
from pathlib import Path

import pytest

from src.aeroplane import Aeroplane
from src.base_saver import AeroplaneStorage, StorageError
from src.json_saver import JSONSaver


def test_aeroplane_storage_is_abstract():
    with pytest.raises(TypeError):
        AeroplaneStorage()  # type: ignore[abstract]


def test_add_aeroplane(tmp_path, aeroplane):
    path = tmp_path / "data" / "aeroplanes.json"
    JSONSaver(path).add_aeroplane(aeroplane)

    assert json.loads(path.read_text(encoding="utf-8")) == [aeroplane.to_dict()]
    assert JSONSaver(path).get_aeroplanes()[0].to_dict() == aeroplane.to_dict()


def test_add_updates_existing_aeroplane(tmp_path, aeroplane):
    saver = JSONSaver(tmp_path / "aeroplanes.json")
    saver.add_aeroplane(aeroplane)
    current = Aeroplane("a1b2c3", "TEST1", "United Kingdom", 250, 11000, False)
    saver.add_aeroplane(current)

    assert [item.to_dict() for item in saver.get_aeroplanes()] == [current.to_dict()]


def test_filter_aeroplanes_by_country(tmp_path, aeroplane):
    saver = JSONSaver(tmp_path / "aeroplanes.json")
    other = Aeroplane("a1b2c4", "TEST2", "France", 220, 9600, False)
    saver.save_snapshot([aeroplane, other])

    assert [item.icao24 for item in saver.get_aeroplanes(" united KINGDOM ")] == [aeroplane.icao24]
    assert saver.get_aeroplanes("United") == []
    with pytest.raises(ValueError, match="страну регистрации"):
        saver.get_aeroplanes(" ")


def test_delete_aeroplane(tmp_path, aeroplane):
    path = tmp_path / "aeroplanes.json"
    saver = JSONSaver(path)
    saver.add_aeroplane(aeroplane)
    saver.add_aeroplane(Aeroplane("a1b2c4", None, "France", None, None, True))

    assert saver.delete_aeroplane(" A1B2C3 ") is True
    assert saver.delete_aeroplane("a1b2c3") is False
    assert [item.icao24 for item in JSONSaver(path).get_aeroplanes()] == ["a1b2c4"]


def test_read_missing_file(tmp_path):
    path = tmp_path / "aeroplanes.json"

    assert JSONSaver(path).get_aeroplanes() == []
    assert not path.exists()


@pytest.mark.parametrize("content", ["{", "{}", "[{}]", '[{"icao24": "bad"}]'])
def test_read_invalid_file(tmp_path, content):
    path = tmp_path / "aeroplanes.json"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(StorageError):
        JSONSaver(path).get_aeroplanes()

    assert path.read_text(encoding="utf-8") == content


def test_failed_write_preserves_previous_snapshot(tmp_path, aeroplane, monkeypatch):
    path = tmp_path / "aeroplanes.json"
    saver = JSONSaver(path)
    saver.save_snapshot([aeroplane])

    def deny_replace(self, target):
        raise PermissionError

    monkeypatch.setattr(Path, "replace", deny_replace)
    with pytest.raises(StorageError, match="записать"):
        saver.save_snapshot([])

    assert [item.icao24 for item in saver.get_aeroplanes()] == [aeroplane.icao24]
    assert list(tmp_path.iterdir()) == [path]
