from unittest.mock import Mock

import pytest

from src.aeroplane import Aeroplane
from src.api import APIError, AircraftAPI
from src.base_saver import AeroplaneStorage
from src.cli import get_top_aeroplanes, user_interaction


@pytest.fixture
def api():
    client = Mock(spec=AircraftAPI)
    client.get_aeroplanes.return_value = [["a1b2c3", "TEST1", "United Kingdom", None, None, 7, 46, 9000, False, 240]]
    return client


@pytest.fixture
def storage(aeroplane):
    saver = Mock(spec=AeroplaneStorage)
    saver.get_aeroplanes.return_value = [aeroplane]
    return saver


def test_top_aeroplanes_by_altitude(aeroplane):
    high = Aeroplane("a1b2c4", "TEST2", "France", 200, 12000, False)
    low = Aeroplane("a1b2c5", "TEST3", "Spain", 270, 7000, False)
    unknown = Aeroplane("a1b2c6", None, "Spain", None, None, True)
    aeroplanes = [low, unknown, high, aeroplane]

    assert get_top_aeroplanes(aeroplanes, 2) == [high, aeroplane]
    assert get_top_aeroplanes(aeroplanes, 10) == [high, aeroplane, low]
    assert get_top_aeroplanes([unknown], 1) == []
    with pytest.raises(ValueError):
        get_top_aeroplanes(aeroplanes, 0)


def test_user_interaction_top_retries_invalid_input(api, storage, monkeypatch, capsys):
    answers = iter([" ", " Switzerland ", "5", "1", "", "two", "0", "-1", "2", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))

    user_interaction(api, storage)

    api.get_aeroplanes.assert_called_once_with("Switzerland")
    assert storage.save_snapshot.call_args.args[0][0].callsign == "TEST1"
    out = capsys.readouterr().out
    assert "Введите название страны" in out
    assert "Такого пункта нет" in out
    assert out.count("Введите целое число больше нуля") == 4
    assert "TEST1 (a1b2c3)" in out


def test_user_interaction_filters_by_country(api, storage, monkeypatch, capsys):
    answers = iter(["Switzerland", "2", " United Kingdom ", "2", "Japan", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    storage.get_aeroplanes.side_effect = [storage.get_aeroplanes.return_value, []]

    user_interaction(api, storage)

    assert [call.args[0] for call in storage.get_aeroplanes.call_args_list] == ["United Kingdom", "Japan"]
    out = capsys.readouterr().out
    assert "TEST1 (a1b2c3)" in out
    assert "Самолёты с такой страной регистрации не найдены" in out


def test_user_interaction_without_altitude(api, storage, monkeypatch, capsys):
    answers = iter(["Switzerland", "1", "2", "0"])
    monkeypatch.setattr("builtins.input", lambda prompt: next(answers))
    storage.get_aeroplanes.return_value = [Aeroplane("a1b2c3", None, "Switzerland", None, None, True)]

    user_interaction(api, storage)

    assert "нет данных о высоте" in capsys.readouterr().out


def test_user_interaction_without_aeroplanes(api, storage, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: "Switzerland")
    api.get_aeroplanes.return_value = []

    user_interaction(api, storage)

    storage.save_snapshot.assert_called_once_with([])
    assert "самолёты не найдены" in capsys.readouterr().out


def test_user_interaction_handles_api_error(api, storage, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda prompt: "Switzerland")
    api.get_aeroplanes.side_effect = APIError("OpenSky не ответил вовремя.")

    user_interaction(api, storage)

    storage.save_snapshot.assert_not_called()
    assert "OpenSky не ответил вовремя" in capsys.readouterr().out


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_user_interaction_ends_cleanly(api, storage, monkeypatch, capsys, error):
    monkeypatch.setattr("builtins.input", Mock(side_effect=error))

    user_interaction(api, storage)

    assert "Работа завершена" in capsys.readouterr().out
