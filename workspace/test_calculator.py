import pytest
from calculator import add, subtract, multiply, divide


def test_add():
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(-2, -3) == -5
    assert add(1.5, 2.5) == 4.0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(3, 5) == -2
    assert subtract(-1, -1) == 0
    assert subtract(5.5, 2.0) == 3.5


def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 3) == -6
    assert multiply(-2, -4) == 8
    assert multiply(5, 0) == 0
    assert multiply(2.5, 2) == 5.0


def test_divide():
    assert divide(10, 2) == 5.0
    assert divide(7, 2) == 3.5
    assert divide(-6, 3) == -2.0
    assert divide(-9, -3) == 3.0


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(10, 0)
