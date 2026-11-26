# Поиск самолётов

## Цель проекта

Консольная программа получает координаты выбранной страны из Nominatim и запрашивает у OpenSky самолёты в этой области. Программа сохраняет выборку в JSON, выводит топ по барометрической высоте и фильтрует записи по стране регистрации.

Область поиска имеет форму прямоугольника, поэтому в выдачу могут попасть самолёты над соседними странами. Страна регистрации в выводе соответствует полю `origin_country`, которое OpenSky определяет по адресу транспондера. В выборке могут быть самолёты на земле и в воздухе.

## Установка и запуск

Нужны Python 3.14 и Poetry. Клонируйте репозиторий и установите зависимости из корня проекта.

```bash
poetry install
poetry run python main.py
```

Введите страну для поиска, например `Switzerland`. После загрузки выберите действие в меню.

- `1` — вывести топ N. Введите целое число больше нуля. Самолёты выводятся по убыванию высоты, записи без высоты пропускаются.
- `2` — отфильтровать самолёты по стране регистрации. Введите полное название из OpenSky, например `United Kingdom`. Регистр букв не влияет на результат.
- `0` — выйти из программы.

Результат последней успешной загрузки хранится в `data/aeroplanes.json`. Если запрос завершился ошибкой, предыдущая выборка сохраняется. Скорость указана в м/с, высота — в метрах.

### Доступ к OpenSky

У OpenSky есть анонимный доступ к текущим данным с лимитом запросов. Если у вас есть API-клиент OpenSky, скопируйте шаблон в `.env` и укажите `OPENSKY_CLIENT_ID` и `OPENSKY_CLIENT_SECRET`. Оба значения можно оставить пустыми для анонимных запросов.

```bash
cp .env.example .env
```

## Структура проекта

- `src/api.py` — абстрактный интерфейс и клиент Nominatim и OpenSky.
- `src/aeroplane.py` — модель самолёта с валидацией и методами сравнения по скорости и высоте.
- `src/base_saver.py` и `src/json_saver.py` — интерфейс хранилища и его JSON-реализация.
- `src/cli.py` и `main.py` — консольное меню и точка запуска.
- `tests/` — тесты модели, API, хранилища и консоли.

### Пример работы с JSON

```python
from src.aeroplane import Aeroplane
from src.json_saver import JSONSaver

saver = JSONSaver("data/example.json")
aeroplane = Aeroplane("a1b2c3", "TEST1", "United Kingdom", 240.0, 9000.0, False)

saver.add_aeroplane(aeroplane)
for item in saver.get_aeroplanes("United Kingdom"):
    print(item)
saver.delete_aeroplane(aeroplane.icao24)
```

## Тесты и проверка кода

В тестах ответы API подменяются, а JSON создаётся во временной папке.

```bash
poetry run python -m pytest --cov=src --cov=main --cov-report=term-missing --cov-fail-under=70
poetry run black --check src tests main.py
poetry run isort --check-only src tests main.py
poetry run flake8 src tests main.py
poetry run mypy src tests main.py
```

## Источники данных

Границы области поиска предоставлены © OpenStreetMap contributors. Публичный Nominatim используется при ручном запросе страны из консоли. Клиент отправляет свой `User-Agent`, выдерживает интервал между запросами и сохраняет найденные координаты на время работы. Для смены сервера задайте полный URL поиска в `NOMINATIM_URL`. [Документация Nominatim](https://nominatim.org/release-docs/develop/api/Search/), [правила использования публичного сервера](https://operations.osmfoundation.org/policies/nominatim/), [лицензия OpenStreetMap](https://www.openstreetmap.org/copyright).

Данные о самолётах предоставляет OpenSky Network. [Документация OpenSky REST API](https://openskynetwork.github.io/opensky-api/rest.html).
