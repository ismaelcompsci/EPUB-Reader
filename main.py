import time
from PySide6.QtWidgets import *
from qframelesswindow import FramelessWindow, StandardTitleBar
from PySide6.QtGui import *
from PySide6.QtCore import *

import sys

import hashlib

from components.book_view import EReader
from components.title_bar import MyTitleBar

path_ = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\epubs\the_blade_itself.epub"
temp = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\temp"

with open(path_, "rb") as current_book:
    first_bytes = current_book.read(1024 * 32)

file_md5 = hashlib.md5(first_bytes).hexdigest()


class EWindow(FramelessWindow):
    def __init__(self, filepath, temp, file_md5):
        super().__init__()

        self.filePath = filepath
        self.temp = temp
        self.file_md5 = file_md5

        self.__setLayout()  # SET LAYOUT

    # SET LAYOUT OF FRAMLESSWINDOW
    def __setLayout(self) -> None:
        self.layout_ = QVBoxLayout()
        self.layout_.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.content_view = EReader(self.filePath, self.temp, self.file_md5)
        self.content_view.load_book()
        self.content_view.set_content(0)

        self.layout_.addWidget(self.content_view)

        self.setLayout(self.layout_)

        self.setTitleBar(
            MyTitleBar(self, self.content_view.this_book[self.file_md5]["cover"])
        )
        self.titleBar.raise_()

        self.content_view.setFocus()
        self.content_view.setStyleSheet("border: 0px")
        # self.content_view.document().setDefaultStyleSheet(
        #     "p { text-indent: 27px; font-family: Helvetica, Arial; font-size: 20px} "
        # )

    def next_chapter(self):
        self.content_view.change_chapter(1)

    def back_chapter(self):
        self.content_view.change_chapter(-1)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainwindow = EWindow(path_, temp, file_md5)

    mainwindow.show()
    mainwindow.setMinimumSize(600, 300)
    mainwindow.resize(500, 900)

    app.exec()
