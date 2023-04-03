import hashlib
import os

import PySide6
from bs4 import BeautifulSoup
from epub_tools.epub import ParseEPUB
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qframelesswindow import *

from utils.utils import resize_image, add_css_to_html


# DISPLAYS HTML FROM BOOK
class EReader(QTextBrowser):
    def __init__(self, path, temp, file_md5):
        super().__init__()

        self.filepath = path
        self.temppath = temp

        self.file_md5 = file_md5

        self.setMouseTracking(True)
        self.setReadOnly(True)
        self.setOpenLinks(False)
        self.verticalScrollBar().setSingleStep(3)

        # self.verticalScrollBar().sliderMoved.connect(self.record_position)

    def load_book(self) -> None:

        book = ParseEPUB(self.filepath, self.temppath, self.file_md5)
        # TODO
        # CHECK IF BOOK ALREADY EXISTS
        # GET DATA FROM DATABASE

        # TODO
        # IF NEW BOOK
        # ADD TO DATABASE

        book.read_book()  # INITIALIZE BOOK
        metadata = book.generate_metadata()  # FOR ADDING TO DB
        toc, content, images_only = book.generate_content()  # FOR READING

        self.this_book = {}

        self.this_book[self.file_md5] = {
            "hash": self.file_md5,
            "path": self.filepath,
        }

        cover_image = resize_image(metadata.cover)

        self.this_book[self.file_md5]["position"] = {}
        self.this_book[self.file_md5]["bookmarks"] = None
        self.this_book[self.file_md5]["toc"] = toc
        self.this_book[self.file_md5]["content"] = content
        self.this_book[self.file_md5]["cover"] = cover_image
        self.this_book[self.file_md5]["title"] = metadata.title
        self.this_book[self.file_md5]["author"] = metadata[1]
        self.this_book[self.file_md5]["year"] = metadata[2]
        self.this_book[self.file_md5]["isbn"] = metadata[3]
        self.this_book[self.file_md5]["tags"] = metadata[4]

    def set_content(self, position) -> None:

        try:

            content = self.this_book[self.file_md5]["content"][position]
            # print(content)

        except IndexError:
            return

        self.this_book[self.file_md5]["position"]["current_chapter"] = position
        self.this_book[self.file_md5]["position"]["is_read"] = False

        self.setHtml(content)

        self.setSearchPaths(
            [
                os.path.join(self.temppath, self.file_md5),
                os.path.join(self.temppath, self.file_md5, "OEBPS", "images"),
                os.path.join(self.temppath, self.file_md5, "OEBPS"),
            ]
        )
        self.setFocus()

    def change_chapter(self, direction) -> None:
        current_position = self.this_book[self.file_md5]["position"]["current_chapter"]
        final_position = len(self.this_book[self.file_md5]["content"])

        # PREVENT SCROLLING BELOW PAGE 1
        if current_position == 0 and direction == -1:
            return

        # PREVENT SCROLLING BEYOND LAST PAGE
        if current_position == final_position and direction == 1:
            return

        self.set_content(current_position + direction)

    def keyPressEvent(self, ev):
        key = ev.key()

        if key == Qt.Key.Key_Right:
            self.change_chapter(1)
        if key == Qt.Key.Key_Left:
            self.change_chapter(-1)

        return super().keyPressEvent(ev)
