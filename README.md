# Ecommerce

Учебный проект с классами товаров и категорий.

Классы `Product` и `Category` находятся в `src/`. Файл `main.py` импортирует их
и показывает пример использования.

## Возможности

- `Product` хранит название, описание, цену и количество товара на складе.
- `Category` хранит название, описание и список товаров.
- `Category.category_count` хранит общее число созданных категорий.
- `Category.product_count` хранит общее число товаров в списках созданных категорий. Количество единиц на складе при этом не суммируется.

## Запуск

```bash
poetry install --no-root
poetry run python main.py
```

## Тесты

```bash
poetry run python -m pytest
```

Для обновления отчета о покрытии в `htmlcov/`:

```bash
poetry run python -m pytest --cov=src --cov-report=term-missing --cov-report=html
```
