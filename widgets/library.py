import base64
import logging

from config.config import TEMPDIR
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractScrollArea,
    QLabel,
    QMenu,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)
from tinydb import TinyDB
from utils.utils import get_items_from_database

from .bookhandler import BookHandler
from .reader import ReaderWindow

logger = logging.getLogger(__name__)


class LibraryWidget(QTableWidget):
    """
    Table view for books aka Library
    """

    def __init__(self, parent: QWidget, db: TinyDB):
        super().__init__(parent)
        self.database = db

        # GRID SETTINGS
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setMaximumWidth(100)
        self.setShowGrid(False)
        self.horizontalHeader().hide()
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        # self.verticalScrollBar().setSingleStep(9)

        self.cellDoubleClicked.connect(self.book_selected)  # REPLACE

        self.create_library()

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def create_library(self):
        """
        Populate table Widget
        """
        logger.info("Creating Library")

        books = get_items_from_database(self.database)

        self.setRowCount(len(books))
        self.setColumnCount(5)

        try:
            for i in range(self.rowCount()):
                for j in range(self.columnCount()):
                    lb = LibraryItem(books[i][j], self)
                    self.setCellWidget(i, j, lb)

        except IndexError:
            pass

        self.resizeColumnsToContents()
        self.resizeRowsToContents()

        logger.info("Done creating library")

    def book_selected(self, row: int, column: int, action: str = "open") -> None:
        """
        Open selected book
        """

        book = self.cellWidget(row, column)

        if book:
            logger.info(f"Book: {book.metadata['title']}")

            file_md5 = book.book_md5
            filepath = book.metadata["path"]

            if action == "open":
                temp_ = TEMPDIR
                self.ewindow = ReaderWindow(
                    filepath,
                    temp_,
                    file_md5,
                    book.metadata,
                    self.database,
                    self,
                )

                logger.info("Showing ReaderWindow")
                self.ewindow.show()

            if action == "delete":
                # DELETE BOOK FROM DB, TEMP, COVER
                handle = BookHandler(filepath, temp_dir=TEMPDIR, database=self.database)
                handle.delete_book()
                self.clear()
                self.create_library()

                logger.info(f"Deleting book: {book.metadata['title']}")

    def book_added(self, file: str) -> None:
        """
        Adds book the database and reloads table widget
        """
        if not file:
            return

        handle = BookHandler(file, TEMPDIR, self.database)
        is_read = handle.read_book()

        logger.info("Added book")

        if not is_read:
            return

        handle.save_book()
        logger.info("Saved Book")

        self.clear()
        self.create_library()

    def contextMenuEvent(self, event):
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


class LibraryItem(QWidget):
    """
    Cell Widget for Library
    """

    def __init__(self, metadata: dict, parent: QWidget) -> None:
        super().__init__(parent)

        self.metadata = metadata
        self.book_md5 = self.metadata["hash"]
        self.book_title = self.metadata["title"]
        self.book_cover = base64.b64decode(self.metadata["cover"])

        # BOOK COVER
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.book_cover)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.lb_pixmap = QLabel(self)
        self.lb_text = QLabel(self)
        self.lb_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lb_text.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

        self.layout().addWidget(self.lb_pixmap)
        self.layout().addWidget(self.lb_text)

        self.init_ui()

    def init_ui(self):
        """
        Set Image into Label
        """
        pix = self.pixmap.scaled(
            100, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )

        self.lb_pixmap.setPixmap(pix)
        if isinstance(self.book_title, dict):
            try:
                self.book_title = self.book_title["#text"]
            except:
                self.book_title = ""

        self.lb_text.setText(self.book_title)

    def img(self):
        return self.book_cover

    def total(self, value):
        if self.book_cover == value:
            return
        self.book_cover = value
        self.initUi()

    def text(self):
        return self.book_title

    def text(self, value):
        if self.book_title == value:
            return
        self.book_title = value
        self.initUi()
