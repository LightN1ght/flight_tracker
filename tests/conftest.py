import pytest

from src.aeroplane import Aeroplane


@pytest.fixture
def aeroplane():
    return Aeroplane("a1b2c3", " TEST1 ", "United Kingdom", 240, 9000, False)
