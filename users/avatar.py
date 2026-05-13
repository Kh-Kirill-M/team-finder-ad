"""Генерация аватарки по умолчанию: первая буква имени на однотонном фоне."""
import io
import random
import uuid

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


AVATAR_SIZE = 256

PALETTE = [
    (66, 103, 178),
    (52, 168, 83),
    (219, 68, 55),
    (244, 180, 0),
    (162, 89, 255),
    (255, 140, 0),
    (0, 153, 153),
    (199, 21, 133),
    (47, 79, 79),
    (220, 20, 60),
    (70, 130, 180),
    (210, 105, 30),
]


def _pick_font(size):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except OSError:
            return ImageFont.load_default()


def generate_avatar(letter):
    """Возвращает ContentFile с PNG-аватаркой."""
    letter = (letter or "?").strip().upper()[:1] or "?"
    bg = random.choice(PALETTE)
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), color=bg)
    draw = ImageDraw.Draw(image)
    font = _pick_font(AVATAR_SIZE // 2)

    try:
        bbox = draw.textbbox((0, 0), letter, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        offset_x, offset_y = bbox[0], bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(letter, font=font)
        offset_x = offset_y = 0

    pos = (
        (AVATAR_SIZE - text_w) // 2 - offset_x,
        (AVATAR_SIZE - text_h) // 2 - offset_y,
    )
    draw.text(pos, letter, fill=(255, 255, 255), font=font)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    name = f"avatar_{uuid.uuid4()}.png"
    return name, ContentFile(buf.read())
