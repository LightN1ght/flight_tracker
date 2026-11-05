import pytest
from src.product import Product

@pytest.fixture()
def product():
    return Product(
        "Samsung Galaxy S23 Ultra", "256GB, Серый цвет, 200MP камера", 180000.0, 5
    )