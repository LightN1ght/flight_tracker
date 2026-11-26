from src.aeroplane import Aeroplane
from src.api import AircraftAPI, APIError
from src.base_saver import AeroplaneStorage, StorageError


def get_top_aeroplanes(aeroplanes: list[Aeroplane], top_n: int) -> list[Aeroplane]:
    """Возвращает топ самолётов с известной высотой по убыванию."""
    if top_n <= 0:
        raise ValueError("Количество самолётов должно быть больше нуля.")

    by_altitude = [
        (altitude, aeroplane) for aeroplane in aeroplanes if (altitude := aeroplane.baro_altitude) is not None
    ]
    by_altitude.sort(key=lambda item: item[0], reverse=True)
    return [aeroplane for _, aeroplane in by_altitude[:top_n]]


def _read_country(prompt: str) -> str:
    while True:
        country = input(prompt).strip()
        if country:
            return country
        print("Программа: Введите название страны.")


def _read_top_count() -> int:
    while True:
        value = input("Введите количество самолётов для вывода в топ: ")
        try:
            top_n = int(value)
        except ValueError:
            top_n = 0
        if top_n > 0:
            return top_n
        print("Программа: Введите целое число больше нуля.")


def user_interaction(api: AircraftAPI, storage: AeroplaneStorage) -> None:
    """Загружает самолёты и предлагает вывести топ или отфильтровать записи."""
    try:
        print("Программа: Привет! Добро пожаловать в программу поиска самолётов.")
        country = _read_country("Введите страну для поиска самолётов: ")
        states = api.get_aeroplanes(country)
        aeroplanes = Aeroplane.cast_to_object_list(states)
        storage.save_snapshot(aeroplanes)
        print("Границы области: © OpenStreetMap contributors.")

        if not aeroplanes:
            print(f"Программа: В области «{country}» самолёты не найдены.")
            return

        print(f"Программа: Результаты поиска для «{country}» сохранены.")
        while True:
            print("\n1. Вывести топ самолётов по высоте\n2. Найти самолёты по стране регистрации\n0. Выйти")
            user_choice = input("Пользователь: ").strip()

            if user_choice == "1":
                top_n = _read_top_count()
                results = get_top_aeroplanes(storage.get_aeroplanes(), top_n)
                if not results:
                    print("Программа: У самолётов в выборке нет данных о высоте.")
                    continue
            elif user_choice == "2":
                origin_country = _read_country("Введите страну регистрации, например United Kingdom: ")
                results = storage.get_aeroplanes(origin_country)
                if not results:
                    print("Программа: Самолёты с такой страной регистрации не найдены.")
                    continue
            elif user_choice == "0":
                return
            else:
                print("Программа: Такого пункта нет в меню.")
                continue

            print(f"Программа: Самолётов в результате: {len(results)}")
            for aeroplane in results:
                print(aeroplane)
    except (APIError, StorageError, ValueError) as error:
        print(f"Программа: {error}")
    except EOFError, KeyboardInterrupt:
        print("\nПрограмма: Работа завершена.")
