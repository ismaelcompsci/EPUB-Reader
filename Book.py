import os
import sys
from turtle import pos


from epub.epub import ParseEPUB
from bs4 import BeautifulSoup
import hashlib

from PySide6.QtWidgets import *
from qframelesswindow import *
from PySide6.QtCore import *

# title = None
# author = None
# year = None
# isbn = None
# tags = None
# position = None
# bookmarks = None
# cover = None

# file_md5 = None
# path = None
# temp = None

# toc = None
# content = None


# def do():
#     path = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\epubstest\Old Man's War - John Scalzi.epub"
#     temp = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\temp"

#     with open(path, "rb") as current_book:
#         first_bytes = current_book.read(1024 * 32)

#     file_md5 = hashlib.md5(first_bytes).hexdigest()

#     book = ParseEPUB(path, temp, file_md5)

#     book.read_book()  # INITIALIZE BOOK
#     metadata = book.generate_metadata()  # FOR ADDING TO DB
#     toc, content, images_only = book.generate_content()  # FOR READING

#     title = metadata.title
#     author = metadata[1]
#     year = metadata[2]
#     isbn = metadata[3]
#     tags = metadata[4]
#     position = None
#     bookmarks = None
#     cover = metadata.cover

#     file_md5 = str(file_md5)


def addCssToHtml(css, html) -> str:

    soup = BeautifulSoup(html, "html.parser")
    style_tag = soup.new_tag("style")
    style_tag.string = css
    soup.head.append(style_tag)
    return str(soup)


# DISPLAYS HTML FROM BOOK
class EReader(QTextBrowser):
    def __init__(self, path, temp, file_md5):
        super().__init__()

        self.filepath = path
        self.temppath = temp

        self.file_md5 = file_md5

        self.setMouseTracking(True)
        self.setReadOnly(True)

        # self.setOpenLinks(False)

        # self.verticalScrollBar().sliderMoved.connect(self.record_position)

    def load_book(self):

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

        self.this_book[self.file_md5]["position"] = {}
        self.this_book[self.file_md5]["bookmarks"] = None
        self.this_book[self.file_md5]["toc"] = toc
        self.this_book[self.file_md5]["content"] = content
        self.this_book[self.file_md5]["cover"] = metadata.cover
        self.this_book[self.file_md5]["title"] = metadata.title
        self.this_book[self.file_md5]["author"] = metadata[1]
        self.this_book[self.file_md5]["year"] = metadata[2]
        self.this_book[self.file_md5]["isbn"] = metadata[3]
        self.this_book[self.file_md5]["tags"] = metadata[4]

    def set_content(self, position):

        try:

            content = self.this_book[self.file_md5]["content"][position]

        except IndexError:
            return

        self.this_book[self.file_md5]["position"]["current_chapter"] = position
        self.this_book[self.file_md5]["position"]["is_read"] = False

        self.setHtml(content)

    def change_chapter(self, direction):
        current_position = self.this_book[self.file_md5]["position"]["current_chapter"]
        final_position = len(self.this_book[self.file_md5]["content"])

        # PREVENT SCROLLING BELOW PAGE 1
        if current_position == 1 and direction == -1:
            return

        # PREVENT SCROLLING BEYOND LAST PAGE
        if current_position == final_position and direction == 1:
            return

        self.set_content(current_position + direction)

    def keyPressEvent(self, ev) -> None:
        key = ev.key()

        if key == Qt.Key.Key_Right:
            self.change_chapter(1)
        if key == Qt.Key.Key_Left:
            self.change_chapter(-1)

        return super().keyPressEvent(ev)
