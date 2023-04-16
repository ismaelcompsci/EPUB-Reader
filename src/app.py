import os
import sys
import logging
import qdarkstyle

from tinydb import TinyDB, Query, where

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
    QMenu,
)
from qframelesswindow import FramelessWindow, StandardTitleBar

from utils.utils import get_image_from_database, create_or_check


# TODO
# LOOK AT FRAMELESSWINDOW EVENTFILTER


# ON BOOK CLICK OPEN WINDOW AT LAST LOCATION AND SIZE
#     - 1ST OPEN AT LAST CHAPTER
#     - 2ND SCROLL TO LAST POSITION

logger = logging.getLogger(__name__)

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

    def __init__(self, parent: QWidget, db: TinyDB) -> None:
        super().__init__(parent)

        self.db = db

        # GRID SETTINGS
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

        self.verticalScrollBar().setSingleStep(1)

    def create_library(self) -> None:
        """
        Populate table widget
        """

        images = get_image_from_database(os.path.join(TEMPDIR, "db"), self.db)

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

    def book_selected(self, row: int, column: int, action: str = "open") -> None:
        """
        Open selected book
        """
        book = self.cellWidget(row, column)

        if book:
            file_md5 = book.file_md5
            filepath = book.full_metadata["path"]

            if action == "open":
                temp_ = TEMPDIR
                ewindow = EWindow(
                    filepath,
                    temp_,
                    file_md5,
                    book.full_metadata,
                    self.db,
                    self,
                )

                ewindow.show()

            if action == "delete":
                # DELETE BOOK FROM DB, TEMP, COVER
                handle = BookHandler(filepath, temp_dir=TEMPDIR, database=self.db)
                handle.delete_book()
                self.clear()
                self.create_library()

    def book_added(self, file: str) -> None:
        """
        Adds book the database and reloads table widget
        """
        if not file:
            return

        handle = BookHandler(file, temp_dir=TEMPDIR, database=self.db)
        is_read = handle.read_book()

        if not is_read:
            return

        handle.save_book()

        self.clear()
        self.create_library()

    def contextMenuEvent(self, event) -> None:
        if self.selectionModel().selection().indexes():
            for i in self.selectionModel().selection().indexes():
                row, column = i.row(), i.column()
            menu = QMenu()
            open_action = menu.addAction("Open")
            delete_action = menu.addAction("Delete")
            action = menu.exec(self.mapToGlobal(event.pos()))

            if action == open_action:
                self.book_selected(row, column, "open")

            if action == delete_action:
                self.book_selected(row, column, "delete")


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

        self.library_view = Library(self, self.db)

        self.v_layout.addWidget(self.library_view)

        self.add_book = QPushButton("Add Book")
        self.add_book.clicked.connect(self.add_book_clicked)
        self.v_layout.addWidget(
            self.add_book, stretch=0, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        # self.v_layout.setContentsMargins(0, 10, 0, 0)

        self.v_layout.setContentsMargins(0, 10, 0, 0)
        self.setLayout(self.v_layout)

        self.titlebar = MainTitleBar(self)
        self.setTitleBar(self.titlebar)
        self.titlebar.raise_()

        self.setContentsMargins(0, 22, 0, 0)

        self.gui_funcitons = MainGuiStyle(self)
        self.gui_funcitons.default_ui()

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def add_book_clicked(self) -> None:
        """
        Opens book
        """
        file_name = QFileDialog.getOpenFileName(
            self,
            "Open EPUB",
            filter="EPUB Files (*.epub)",
        )[0]

        self.library_view.book_added(file_name)
        # if len(file_names) == 1:
        #     self.library_view.book_added(file_names[0])
        # else:
        #     self.library_view.multiple_books_added(file_names)


class MainGuiStyle:
    def __init__(self, parent: QWidget):
        super().__init__()
        self.main_window = parent
        self.library_view = self.main_window.library_view
        self.main_titlebar = self.main_window.titlebar

    def default_ui(self):
        self.library_view.setStyleSheet(
            """
            QTableWidget {border-width: 0px; border-style: solid}
            """
        )

    # def dark(self):
    #     # MAIN WINDOW DARK
    #     self.main_window.setStyleSheet(
    #         """ * {background-color: #18191A; color: #FFFFFF;} """
    #     )

    #     # TITLE BAR DARK
    #     self.main_titlebar.closeBtn.setNormalColor("#FFFFFF")
    #     self.main_titlebar.minBtn.setNormalColor("#FFFFFF")
    #     self.main_titlebar.maxBtn.setNormalColor("#FFFFFF")
    #     self.main_titlebar.setStyleSheet("color: white;")

    #     self.library_view.setStyleSheet(
    #         """
    #         QTableWidget::item{ selection-background-color: #161618;}
    #         QTableWidget {border-width: 0px; border-style: solid}
    #         """
    #     )


class MainTitleBar(StandardTitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.setTitle("EPUB Reader")


if __name__ == "__main__":
    # Create the QApplication object
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    mainwindow = MainWindow(database=db, query=BooksQ)
    mainwindow.show()
    app.exec()
