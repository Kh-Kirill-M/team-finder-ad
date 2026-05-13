import re
from urllib.parse import urlparse

from django.core.exceptions import ValidationError

PHONE_RE = re.compile(r"^(?:8|\+7)\d{10}$")


def normalize_phone(value):
    """Привести телефон к формату +7XXXXXXXXXX."""
    if not value:
        return value
    cleaned = re.sub(r"\s+", "", value)
    if not PHONE_RE.match(cleaned):
        return cleaned
    if cleaned.startswith("8"):
        cleaned = "+7" + cleaned[1:]
    return cleaned


def validate_phone(value):
    cleaned = re.sub(r"\s+", "", value or "")
    if not PHONE_RE.match(cleaned):
        raise ValidationError(
            "Телефон должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX."
        )


def validate_github_url(value):
    if not value:
        return
    try:
        parsed = urlparse(value)
    except ValueError as exc:
        raise ValidationError("Некорректная ссылка.") from exc
    if parsed.scheme not in ("http", "https"):
        raise ValidationError("Ссылка должна начинаться с http:// или https://.")
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host != "github.com" and not host.endswith(".github.com"):
        raise ValidationError("Ссылка должна вести на github.com.")
