import pytest

from main import Category, Product


@pytest.fixture()
def category():
    return Category(
        "Смартфоны",
        "Смартфоны, как средство не только коммуникации, но и получения дополнительных функций для удобства жизни",
        ["Samsung", "Vivo", "Pixel"],
    )


@pytest.fixture()
def products():
    return Product(
        "Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5
    )


def test_init_category(category):
    assert category.name == "Смартфоны"
    assert (
        category.description
        == "Смартфоны, как средство не только коммуникации, но и получения дополнительных функций для удобства жизни"
    )
    assert category.products == ["Samsung", "Vivo", "Pixel"]


def test_init_products(products):
    assert products.name == "Samsung Galaxy S23 Ultra"
    assert products.description == "256GB, Серый цвет, 200MP камера"
    assert products.price == 180000.0
    assert products.quantity == 5


def test_category_count():
    before = Category.category_count
    category = Category("Тест", "Описание", [])

    assert Category.category_count == before + 1
    assert category.category_count == Category.category_count


def test_product_count():
    before = Category.product_count
    category = Category("Тест", "Описание", ["1"])

    assert Category.product_count == before + 1
    assert category.product_count == Category.product_count
