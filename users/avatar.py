"""Генерация аватарки по умолчанию: первая буква имени на однотонном фоне."""
import io
import random
import uuid

from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont


AVATAR_SIZE = 256
FONT_RATIO = 2
FONT_SIZE = AVATAR_SIZE // FONT_RATIO
ANCHOR_ZERO = (0, 0)

TEXT_COLOR_WHITE = (255, 255, 255)
DEFAULT_LETTER = "?"

COLOR_BLUE = (66, 103, 178)
COLOR_GREEN = (52, 168, 83)
COLOR_RED = (219, 68, 55)
COLOR_YELLOW = (244, 180, 0)
COLOR_PURPLE = (162, 89, 255)
COLOR_ORANGE = (255, 140, 0)
COLOR_TEAL = (0, 153, 153)
COLOR_MAGENTA = (199, 21, 133)
COLOR_DARK_SLATE = (47, 79, 79)
COLOR_CRIMSON = (220, 20, 60)
COLOR_STEEL_BLUE = (70, 130, 180)
COLOR_CHOCOLATE = (210, 105, 30)

PALETTE = [
    COLOR_BLUE,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_PURPLE,
    COLOR_ORANGE,
    COLOR_TEAL,
    COLOR_MAGENTA,
    COLOR_DARK_SLATE,
    COLOR_CRIMSON,
    COLOR_STEEL_BLUE,
    COLOR_CHOCOLATE,
]

FONT_CANDIDATES = ("arial.ttf", "DejaVuSans.ttf")
IMAGE_MODE_RGB = "RGB"
IMAGE_FORMAT_PNG = "PNG"
FILENAME_TEMPLATE = "avatar_{uid}.png"


def _pick_font(size):
    for font_name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(font_name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _measure(draw, letter, font):
    try:
        bbox = draw.textbbox(ANCHOR_ZERO, letter, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        offset_x, offset_y = bbox[0], bbox[1]
    except AttributeError:
        width, height = draw.textsize(letter, font=font)
        offset_x = offset_y = 0
    return width, height, offset_x, offset_y


def generate_avatar(letter):
    """Возвращает (filename, ContentFile) с PNG-аватаркой."""
    letter = (letter or DEFAULT_LETTER).strip().upper()[:1] or DEFAULT_LETTER

    background = random.choice(PALETTE)
    image = Image.new(IMAGE_MODE_RGB, (AVATAR_SIZE, AVATAR_SIZE), color=background)
    draw = ImageDraw.Draw(image)
    font = _pick_font(FONT_SIZE)

    width, height, offset_x, offset_y = _measure(draw, letter, font)
    position = (
        (AVATAR_SIZE - width) // 2 - offset_x,
        (AVATAR_SIZE - height) // 2 - offset_y,
    )
    draw.text(position, letter, fill=TEXT_COLOR_WHITE, font=font)

    buf = io.BytesIO()
    image.save(buf, format=IMAGE_FORMAT_PNG)
    buf.seek(0)
    filename = FILENAME_TEMPLATE.format(uid=uuid.uuid4())
    return filename, ContentFile(buf.read())
