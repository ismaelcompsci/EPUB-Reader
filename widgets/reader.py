from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qframelesswindow import FramelessWindow
from tinydb import TinyDB

from .book_view import BookViewer
from config.config import EXTRACTED_EPUB_DIR, DATABASE_DIR, Books


class ReaderInterface(QWidget):
    def __init__(self, parent, metadata):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)

        self.metadata = metadata

        self.book_view = BookViewer(
            self,
            self.metadata["path"],
            EXTRACTED_EPUB_DIR,
            self.metadata["hash"],
            Books,
            self.metadata,
        )

        self.book_view.load_book()
        self.hBoxLayout.addWidget(self.book_view)
