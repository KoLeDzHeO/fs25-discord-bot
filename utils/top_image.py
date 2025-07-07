"""Отрисовка изображений с таблицей топа игроков."""

from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont
import io


FONT = ImageFont.load_default()


def draw_top_image(rows: List[Dict], title: str, size: int, key: str) -> io.BytesIO:
    """Рисует PNG-таблицу топа игроков.

    Args:
        rows: Список строк из базы данных.
        title: Заголовок таблицы.
        size: Количество строк (10 или 50).
        key: Имя колонки со значением часов.
    Returns:
        BytesIO с изображением PNG.
    """
    # Размеры строк и шапки
    header_h = 40
    row_h = 40
    width = 400
    height = header_h + row_h * size

    # Создаём холст
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Заголовок
    draw.rectangle([0, 0, width, header_h], fill=(200, 200, 200))
    draw.text((10, 10), title, font=FONT, fill="black")

    # Рисуем строки
    for i in range(size):
        y = header_h + i * row_h
        # Подложка через одну строку
        if i % 2 == 0:
            draw.rectangle([0, y, width, y + row_h], fill=(240, 240, 240))

        place = str(i + 1)
        if i < len(rows):
            name = rows[i]["player_name"]
            hours = rows[i][key]
        else:
            name = "-"
            hours = "-"

        draw.text((10, y + 10), f"{place}. {name}", font=FONT, fill="black")
        hours_text = f"{hours} ч" if hours != "-" else "-"
        text_w, _ = draw.textsize(hours_text, font=FONT)
        draw.text((width - text_w - 10, y + 10), hours_text, font=FONT, fill="black")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf
