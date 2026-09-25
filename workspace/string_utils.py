def reverse_text(text: str) -> str:
    """Return the reversed string."""
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Return True if the text is a palindrome (case-insensitive or exact), false otherwise."""
    cleaned = text.lower()
    return cleaned == cleaned[::-1]
