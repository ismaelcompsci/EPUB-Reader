import os
import sys

import tinydb

from tinydb import TinyDB, Query

from components.book_view import BookHandler
from components.custom_widgets import CustomWidget
from main_reader_view import EWindow
from PySide6.QtCore import Qt
from PySide6.QtGui import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QApplication,
    QFileDialog,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from qframelesswindow import FramelessWindow, StandardTitleBar
from resources import rc_resources
from utils.utils import get_image_from_database, create_or_check


# TODO
# LOOK AT FRAMELESSWINDOW EVENTFILTER


# ON BOOK CLICK OPEN WINDOW AT LAST LOCATION AND SIZE
#     - 1ST OPEN AT LAST CHAPTER
#     - 2ND SCROLL TO LAST POSITION


BASEDIR = os.path.dirname(__file__)

TEMPDIR = os.path.join(BASEDIR, "temp")
DB_DIR = os.path.join(TEMPDIR, "tinydb")

create_or_check(TEMPDIR)
create_or_check(DB_DIR)

db_ = TinyDB(DB_DIR + "\\Books.json")

db = db_.table("Books")
settings = db_.table("settings")

BooksQ = Query()


class Library(QTableWidget):
    """
    Table view for books
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

        self.db = self.parent().db
        self.query = self.parent().query

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setMaximumWidth(100)

        self.setShowGrid(False)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.verticalScrollBar().setSingleStep(9)

        self.cellDoubleClicked.connect(self.book_selected)

        self.create_library()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        self.setStyleSheet("border-width: 0px; border-style: solid")

    def create_library(self) -> None:
        """
        Populate table widget
        """

        images = get_image_from_database(
            os.path.join(TEMPDIR, "db"), self.db, self.query
        )

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

    def book_selected(self, row: int, column: int) -> None:
        """
        Open selected book
        """
        book = self.cellWidget(row, column)

        if book:
            file_md5 = book.file_md5
            filepath = book.full_metadata["path"]

            temp_ = TEMPDIR
            self.ewindow = EWindow(
                filepath, temp_, file_md5, book.full_metadata, self.db, self.query
            )

            self.reading_book = True

            self.ewindow.show()

    def book_added(self, file: str) -> None:
        """
        Adds book the database and reloads table widget
        """
        handle = BookHandler(file, temp_dir=TEMPDIR, database=self.db, query=self.query)
        handle.read_book()
        handle.save_book()

        self.clear()
        self.create_library()


class MainWindow(FramelessWindow):
    """
    Main view for app
    """

    def __init__(self, database: TinyDB, query: Query) -> None:
        super().__init__()
        self.resize(800, 600)

        self.db = database
        self.query = query

        self.v_layout = QVBoxLayout()

        self.library_view = Library(self)

        self.v_layout.addWidget(self.library_view)

        self.add_book = QPushButton("Add Book")
        self.add_book.clicked.connect(self.add_book_clicked)
        self.v_layout.addWidget(
            self.add_book, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.v_layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(self.v_layout)

        titlebar = StandardTitleBar(self)
        titlebar.setTitle("EPUB Reader")
        self.setTitleBar(titlebar)
        self.titleBar.raise_()

        self.setContentsMargins(0, 22, 0, 0)

    def add_book_clicked(self) -> None:
        """
        Opens book
        """
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open EPUB",
            filter="EPUB Files (*.epub)",
        )[0]

        if file_name:
            self.library_view.book_added(file_name)


if __name__ == "__main__":
    # Create the QApplication object
    app = QApplication(sys.argv)

    mainwindow = MainWindow(database=db, query=BooksQ)
    mainwindow.setStyleSheet("background-color: white")
    mainwindow.show()
    app.exec()
