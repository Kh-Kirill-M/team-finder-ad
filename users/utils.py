"""Утилиты, общие для приложения users."""
import secrets

from .models import User

PLACEHOLDER_PHONE_PREFIX = "+7"
PLACEHOLDER_PHONE_DIGITS = 10
DIGIT_BASE = 10


def make_placeholder_phone():
    """Сгенерировать уникальный placeholder-телефон в формате +7XXXXXXXXXX.

    Используется на регистрации, где телефон ещё не известен,
    но в модели User это поле обязательно и уникально.
    """
    while True:
        tail = "".join(
            str(secrets.randbelow(DIGIT_BASE)) for _ in range(PLACEHOLDER_PHONE_DIGITS)
        )
        candidate = f"{PLACEHOLDER_PHONE_PREFIX}{tail}"
        if not User.objects.filter(phone=candidate).exists():
            return candidate
