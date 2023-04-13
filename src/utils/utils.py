import base64
import copy
import datetime
import hashlib
import io
import json
import os
import pathlib

from bs4 import BeautifulSoup
from tinydb import Query, TinyDB
from epub_tools.epub import ParseEPUB
from PySide6.QtCore import QBuffer, QByteArray, QIODevice
from PySide6.QtGui import QImage, Qt
from PySide6.QtWidgets import QWidget


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


def add_css_to_html(css: str, html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.new_tag("style")
    style_tag.string = css
    soup.head.append(style_tag)
    return str(soup)


def file_md5_(file: str = None) -> str:
    if file:
        with open(file, "rb") as f:
            first_bytes = f.read(1024 * 32)
            file_md5_ = hashlib.md5(first_bytes).hexdigest()

        return file_md5_

    return


def get_image_from_database(db_path: str, db: TinyDB, query: Query) -> list:
    """
    returns a 2d array with a row containing max 5 columns per row
    """

    books = db.all()
    return to_matrix(books, 5)


def to_matrix(l: list, n: int) -> list:
    return [l[i : i + n] for i in range(0, len(l), n)]


def create_or_check(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


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
    # Return the temp dir of the book
    return os.path.join(temp, file_md5) + os.path.join


# DISPLAYS HTML FROM BOOK
class BookHandler:
    """
    Adds book to db
    """

    def __init__(
        self,
        file: str,
        db_path: str = None,
        settings: str = None,
        temp_dir: str = None,
        parent: QWidget = None,
    ) -> None:
        self.parent = parent

        self.file = file
        self.database_path = db_path
        self.settings = settings
        self.temp_dir = temp_dir

    def hash_book(self) -> str:
        md5_ = file_md5_(self.file)
        return md5_

    def read_book(self):
        self.md5_ = self.hash_book()

        # BOOK DATA
        self.parsed_book = ParseEPUB(self.file, self.temp_dir, self.md5_)
        # NEW BOOK
        self.parsed_book.read_book()  # INITIALIZE BOOK
        metadata = self.parsed_book.generate_metadata()  # FOR ADDING TO DB
        toc, content, images_only = self.parsed_book.generate_content()  # FOR READING

        self.this_book = {}

        cover_image = resize_image(metadata.cover)

        self.this_book[self.md5_] = {
            "hash": self.md5_,
            "path": self.file,
            "position": {},
            "bookmarks": None,
            "toc": toc,
            "content": content,
            "cover": cover_image,
            "title": metadata.title,
            "author": metadata[1],
            "year": metadata[2],
            "isbn": metadata[3],
            "tags": metadata[4],
            "date_added": datetime.datetime.now().timestamp() * 1000,
        }

    def save_book(self) -> None:
        """
        Initialize epub file
        """
        # CHECK IF BOOK ALREADY EXISTS
        if f"{self.md5_}.json" in os.listdir(os.path.join(self.temp_dir, "db")):
            return

        # IF NEW BOOK
        # ADD TO DATABASE
        self.save_new_book()

    def save_new_book(self) -> None:
        """
        Saves new book
        """
        new_metadata = copy.deepcopy(self.this_book)
        new_metadata[self.md5_].pop("content")

        # ENCODED IMAGE
        image = base64.b64encode(new_metadata[self.md5_]["cover"]).decode("utf-8")
        # DECODE -> base64.b64decode(encoded_image)

        new_metadata[self.md5_]["cover"] = image

        database_path = os.path.join(self.temp_dir, "db")

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        with open(os.path.join(database_path, f"{self.md5_}.json"), "w") as f:
            json.dump(new_metadata, f)
