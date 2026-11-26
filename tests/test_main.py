import json
from unittest.mock import Mock

import pytest

import main
from src.json_saver import JSONSaver


@pytest.fixture
def output_path(tmp_path, monkeypatch):
    path = tmp_path / "aeroplanes.json"
    monkeypatch.setattr(main, "load_dotenv", Mock())
    monkeypatch.setattr(main, "JSONSaver", lambda: JSONSaver(path))
    for name in ("NOMINATIM_URL", "OPENSKY_CLIENT_ID", "OPENSKY_CLIENT_SECRET"):
        monkeypatch.delenv(name, raising=False)
    return path


def test_main_saves_and_displays_aeroplanes(output_path, monkeypatch, capsys):
    nominatim = Mock()
    nominatim.json.return_value = [{"boundingbox": ["45.8", "47.8", "5.9", "10.5"]}]
    opensky = Mock()
    opensky.json.return_value = {
        "states": [
            ["a1b2c3", "TEST1", "United Kingdom", None, None, 7, 46, 9000, False, 240],
            ["a1b2c4", "TEST2", "France", None, None, 7, 46, 12000, False, 220],
            ["a1b2c5", None, "Switzerland", None, None, 7, 46, None, True, None],
        ]
    }
    request = Mock(side_effect=[nominatim, opensky])
    monkeypatch.setattr("src.api.requests.request", request)
    monkeypatch.setenv("NOMINATIM_URL", "https://nominatim.example/search")
    answers = iter(["Switzerland", "1", "2", "2", "united kingdom", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    main.main()

    records = json.loads(output_path.read_text(encoding="utf-8"))
    assert [record["icao24"] for record in records] == ["a1b2c3", "a1b2c4", "a1b2c5"]
    assert request.call_args_list[0].args[1] == "https://nominatim.example/search"
    out = capsys.readouterr().out
    assert out.index("TEST2 (a1b2c4)") < out.index("TEST1 (a1b2c3)")
    assert out.count("TEST1 (a1b2c3)") == 2
    assert "a1b2c5" not in out
    assert "Высота: 12000.0 м" in out


def test_main_keeps_previous_data_when_all_rows_are_invalid(output_path, aeroplane, monkeypatch, capsys):
    previous_data = [aeroplane.to_dict()]
    JSONSaver(output_path).save_snapshot([aeroplane])
    nominatim = Mock()
    nominatim.json.return_value = [{"boundingbox": ["45.8", "47.8", "5.9", "10.5"]}]
    opensky = Mock()
    opensky.json.return_value = {"states": [["incomplete"]]}
    monkeypatch.setattr("src.api.requests.request", Mock(side_effect=[nominatim, opensky]))
    monkeypatch.setattr("builtins.input", lambda prompt: "Switzerland")

    main.main()

    assert json.loads(output_path.read_text(encoding="utf-8")) == previous_data
    assert "не вернул ни одной корректной записи" in capsys.readouterr().out


def test_main_with_incomplete_credentials(output_path, monkeypatch, capsys):
    monkeypatch.setenv("OPENSKY_CLIENT_ID", "example")

    main.main()

    assert "идентификатор, и секрет клиента" in capsys.readouterr().out
    assert not output_path.exists()
