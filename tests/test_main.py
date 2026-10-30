import pytest

from main import Category, Product


@pytest.fixture()
def category(product):
    return Category(
        "Смартфоны",
        "Смартфоны, как средство не только коммуникации, но и получения дополнительных функций для удобства жизни",
        [product],
    )


@pytest.fixture()
def product():
    return Product(
        "Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5
    )


def test_init_category(category):
    assert category.name == "Смартфоны"
    assert (
        category.description
        == "Смартфоны, как средство не только коммуникации, но и получения дополнительных функций для удобства жизни"
    )
    assert category.products == "Samsung Galaxy S23 Ultra, 180000.0 руб. Остаток: 5 шт."


def test_init_products(product):
    assert product.name == "Samsung Galaxy S23 Ultra"
    assert product.description == "256GB, Серый цвет, 200MP камера"
    assert product.price == 180000.0
    assert product.quantity == 5


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
        "Vivo, 20000.0 руб. Остаток: 14 шт."
    )


def test_products_empty():
    category = Category("Пустая", "", [])
    assert category.products == ""


def test_products_private(category):
    with pytest.raises(AttributeError):
        _ = category.__products


def test_new_product():
    data = {"name": "Vivo", "description": "Синий", "price": 20000.0, "quantity": 14}
    product = Product.new_product(data)

    assert isinstance(product, Product)
    assert product.name == "Vivo"
    assert product.description == "Синий"
    assert product.price == 20000.0
    assert product.quantity == 14


def test_price_private(product):
    with pytest.raises(AttributeError):
        _ = product.__price


def test_price_increase(product, capsys):
    product.price = 200000.0

    assert product.price == 200000.0
    assert capsys.readouterr().out == ""


def test_product_count(product):
    before = Category.product_count
    category = Category("Тест", "Описание", [product])

    assert Category.product_count == before + 1
    assert category.product_count == Category.product_count


@pytest.mark.parametrize("invalid_price", [0, -5])
def test_price_rejects_nonpositive(product, invalid_price, capsys):
    old_price = product.price
    product.price = invalid_price

    assert product.price == old_price
    assert (
        capsys.readouterr().out.strip()
        == "Цена не должна быть нулевая или отрицательная"
    )
