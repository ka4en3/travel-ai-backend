# app/utils/utils.py

from nanoid import generate


def generate_nanoid_code(size: int = 16) -> str:
    """
    Generate a secure share code using nanoid.
    """
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return generate(alphabet, size)
