import pytest

from src.category import Category
from src.product import Product


@pytest.fixture()
def category(product):
    return Category(
        "Смартфоны",
        "Смартфоны, как средство не только коммуникации, но и получения дополнительных функций для удобства жизни",
        [product],
    )


def test_init_category(category):
    assert category.name == "Смартфоны"
    assert (
        category.description
        == "Смартфоны, как средство не только коммуникации, но и получения дополнительных функций для удобства жизни"
    )
    assert (
        category.products == "Samsung Galaxy S23 Ultra, 180000.0 руб. Остаток: 5 шт.\n"
    )


def test_category_str(product):
    second = Product("Vivo", "", 20000.0, 14)
    category = Category("Смартфоны", "", [product, second])

    assert str(category) == "Смартфоны, количество продуктов: 19 шт."


def test_category_count():
    before = Category.category_count
    first = Category("Первая", "", [])
    Category("Вторая", "", [])

    assert Category.category_count == before + 2
    assert first.category_count == Category.category_count


def test_product_count_from_constructor(product):
    before = Category.product_count
    second = Product("Vivo", "", 20000.0, 14)
    Category("Смартфоны", "", [product, second])

    assert Category.product_count == before + 2


def test_add_product(category):
    before = Category.product_count
    second = Product("Vivo", "", 20000.0, 14)
    category.add_product(second)

    assert Category.product_count == before + 1
    assert category.products == (
        "Samsung Galaxy S23 Ultra, 180000.0 руб. Остаток: 5 шт.\n"
        "Vivo, 20000.0 руб. Остаток: 14 шт.\n"
    )


def test_products_empty():
    category = Category("Пустая", "", [])
    assert category.products == ""


def test_products_private(category):
    with pytest.raises(AttributeError):
        _ = category.__products


def test_product_count(product):
    before = Category.product_count
    category = Category("Тест", "Описание", [product])

    assert Category.product_count == before + 1
    assert category.product_count == Category.product_count
