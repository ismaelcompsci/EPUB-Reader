import hashlib
import io
import os
import pathlib

from qtpy.QtCore import QBuffer, QByteArray, QIODevice
from qtpy.QtGui import QImage, Qt
from tinydb import TinyDB


def get_items_from_database(db: TinyDB) -> list:
    """
    returns a 2d array with a row containing max 5 columns per row
    """
    books = db.all()
    return to_matrix(books, 5)


def to_matrix(l: list, n: int) -> list:
    return [l[i : i + n] for i in range(0, len(l), n)]


def create_or_check(path: str) -> str:
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def get_file_md5_hash(path: str) -> str:
    with open(path, "rb") as f:
        first_bytes = f.read(1024 * 32)
        file_md5_ = hashlib.md5(first_bytes).hexdigest()

        return file_md5_


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

    return cover_image_final.getvalue()


def find_html_dir(temp: str, file_md5: str) -> str:
    """
    Find html dir for setHtml baseUrl
    """
    base_dir = os.path.join(temp, file_md5)

    for path, subdirs, files in os.walk(base_dir):
        html_file_count = sum(1 for name in files if "htm" in name)
        if html_file_count >= 2:
            # return a dir with 2 or more html files
            return str(pathlib.Path(path).resolve()) + os.path.sep
        # if html_file_count < 2:
        #     return str(pathlib.Path(path).resolve()) + os.path.sep
    # Return the temp dir of the book
    return os.path.join(temp, file_md5) + os.path.join
