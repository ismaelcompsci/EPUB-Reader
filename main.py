import os
import sys
import logging

import qdarkstyle
from qframelesswindow import FramelessWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QPushButton,
    QVBoxLayout,
)
from tinydb import TinyDB

from config.config import _db
from widgets.titlebars import MainTitleBar
from widgets.library import LibraryWidget

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

db = _db.table("Books")
settings = _db.table("settings")


class MainWindow(FramelessWindow):
    """
    Main view for app
    """

    def __init__(self, database: TinyDB):
        super().__init__()

        self.db = database

        self.v_layout = QVBoxLayout()

        self.library_view = LibraryWidget(self, self.db)

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

        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.resize(800, 600)

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


if __name__ == "__main__":
    # Create the QApplication object
    app = QApplication(sys.argv)

    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    mainwindow = MainWindow(database=db)
    mainwindow.show()
    logger.info("STARTING APP")
    app.exec()
    logger.info("EXITED")
