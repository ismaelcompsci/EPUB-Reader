import hashlib
import io

from bs4 import BeautifulSoup
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QImage, Qt


def resize_image(cover_image_raw: bytes) -> bytes:
    if isinstance(cover_image_raw, QImage):
        cover_image = cover_image_raw
    else:
        cover_image = QImage()
        cover_image.loadFromData(cover_image_raw)

    # RESIZE TO ACCEPTABLE COVER IMAGE SIZE
    cover_image = cover_image.scaled(420, 600, Qt.AspectRatioMode.KeepAspectRatio)

    byte_array = QByteArray()
    buffer = QBuffer(byte_array)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    cover_image.save(buffer, "jpg", 75)

    cover_image_final = io.BytesIO(byte_array)
    cover_image_final.seek(0)
    print(type(cover_image_final.getvalue()))
    return cover_image_final.getvalue()


def add_css_to_html(css: str, html: str) -> str:

    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.new_tag("style")
    style_tag.string = css
    soup.head.append(style_tag)
    return str(soup)


def file_md5_(file: str) -> str:
    with open(file, "rb") as f:
        first_bytes = f.read(1024 * 32)
        file_md5_ = hashlib.md5(first_bytes).hexdigest()

    return file_md5_
