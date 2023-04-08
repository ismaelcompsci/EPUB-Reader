import base64
from fileinput import filename
import json
import os

import PySide6
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import *

from components.book_view import BookHandler
from main_reader_view import EWindow
from qframelesswindow import *
from components.custom_widgets import CustomWidget


from static import rc_resources

BASEDIR = os.path.dirname(__file__)

TEMPDIR = os.path.join(BASEDIR, "temp")

if not os.path.exists(TEMPDIR):
    os.makedirs(TEMPDIR)


# TODO
# PUT NEW CLASSES IN SEPERATE FILES
# IMPLEMENT ADD BOOK BUTTON
# ON BOOK CLICK OPEN WINDOW AT LAST LOCATION AND SIZE
#     - 1ST OPEN AT LAST CHAPTER
#     - 2ND SCROLL TO LAST POSITION


def get_image_from_database(db_path):
    if not os.path.exists(db_path):
        os.makedirs(db_path)

    books = []
    for file in os.listdir(db_path):
        filepath = os.path.join(db_path, file)
        with open(filepath, "r") as f:
            book = json.loads(f.read())
            filehash = os.path.splitext(file)[0]
            books.append({"hash": filehash, "book": book})

    return to_matrix(books, 5)


def to_matrix(l, n):
    return [l[i : i + n] for i in range(0, len(l), n)]


class Library(QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.horizontalHeader().setStretchLastSection(True)
        self.setShowGrid(False)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.cellDoubleClicked.connect(self.book_selected)

        self.create_library()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        self.setStyleSheet("border-width: 0px; border-style: solid")

    def create_library(self):

        images = get_image_from_database(os.path.join(TEMPDIR, "db"))

        self.setRowCount(len(images))
        self.setColumnCount(5)

        # pass images into table
        try:
            for i in range(self.rowCount()):
                for j in range(self.columnCount()):

                    lb = CustomWidget(
                        images[i][j],
                    )
                    self.setCellWidget(i, j, lb)
        except IndexError:
            pass

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def book_selected(self, row, column):
        book = self.cellWidget(row, column)

        file_md5 = book.file_md5
        filepath = book.full_metadata[file_md5]["path"]

        temp_ = TEMPDIR

        ewindow = EWindow(filepath, temp_, file_md5, book.full_metadata)
        ewindow.show()

    def book_added(self, file):
        handle = BookHandler(file, temp_dir=TEMPDIR)
        handle.save_book()

        self.create_library()


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()

        self.resize(800, 600)

        self.v_layout = QVBoxLayout()

        self.table = Library(self)

        self.v_layout.addWidget(self.table)

        self.add_book = QPushButton("Add Book")
        self.add_book.clicked.connect(self.add_book_clicked)
        self.v_layout.addWidget(
            self.add_book, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.v_layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(self.v_layout)
        # self.setCentralWidget(self.table)

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        self.titleBar.raise_()
        self.titleBar.setWindowTitle("EPUB Reader")
        self.setContentsMargins(0, 22, 0, 0)

    def add_book_clicked(self):
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open EPUB",
            filter="EPUB Files (*.epub)",
        )[0]

        self.table.book_added(file_name)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.setStyleSheet("background-color: white")
    mainwindow.show()
    app.exec()
