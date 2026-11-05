import pytest
from src.product import Product

def test_init_products(product):
    assert product.name == "Samsung Galaxy S23 Ultra"
    assert product.description == "256GB, Серый цвет, 200MP камера"
    assert product.price == 180000.0
    assert product.quantity == 5

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

@pytest.mark.parametrize("invalid_price", [0, -5])
def test_price_rejects_nonpositive(product, invalid_price, capsys):
    old_price = product.price
    product.price = invalid_price

    assert product.price == old_price
    assert (
        capsys.readouterr().out.strip()
        == "Цена не должна быть нулевая или отрицательная"
    )

def test_product_str(product):
    assert str(product) == (
        "Samsung Galaxy S23 Ultra, 180000.0 руб. Остаток: 5 шт."
    )


def test_product_add():
    first = Product("Первый", "", 100, 10)
    second = Product("Второй", "", 200, 2)

    assert first + second == 1400