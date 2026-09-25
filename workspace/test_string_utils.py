import pytest
from string_utils import reverse_text, is_palindrome


def test_reverse_text():
    assert reverse_text("hello") == "olleh"
    assert reverse_text("") == ""
    assert reverse_text("a") == "a"


def test_is_palindrome():
    assert is_palindrome("Racecar") is True
    assert is_palindrome("Madam") is True
    assert is_palindrome("hello") is False
    assert is_palindrome("") is True
    assert is_palindrome("A") is True
