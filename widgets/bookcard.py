import base64
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QVBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
)


class BookCover(QLabel):
    def __init__(self, cover):
        super().__init__()
        self.cover = cover
        self.setContentsMargins(0, 0, 0, 0)

        self.set_pixmap(cover)
        

    def set_pixmap(self, cover):
        self.makeCover(cover)
        self.update()

    def makeCover(self, cover: str):
        if cover.startswith(":"):
            pixmap = QPixmap(cover)
            self.setPixmap(pixmap)
        else:
            pixmap = QPixmap()
            bytes_ = base64.b64decode(cover)
            pixmap.loadFromData(bytes_)

        # pix = pixmap.scaled(200, 225, Qt.AspectRatioMode.KeepAspectRatio)
        self.setPixmap(pixmap)
        self.setCursor(Qt.PointingHandCursor)


class BookCard(QFrame):
    clicked = pyqtSignal(dict)

    def __init__(self, metadata: dict, parent):
        super().__init__(parent)
        self.isSelected = False
        self.metadata = metadata

        self.bookCover = BookCover(self.metadata["cover"])
        self.bookTitle = QLabel(self)

        self.vBoxLayout = QVBoxLayout(self)
        # BOOK CARD STYLING
        self.setFixedSize(150, 250)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addWidget(self.bookCover, 1, Qt.AlignmentFlag.AlignHCenter)
        self.vBoxLayout.addSpacing(0)
        self.vBoxLayout.addWidget(self.bookTitle, 0, Qt.AlignmentFlag.AlignHCenter)

        self.bookTitle.setText(self.metadata["title"])
        self.bookCover.setScaledContents(True)

        self.setContentsMargins(0, 0, 0, 0)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event) -> None:
        if self.isSelected:
            return
        self.clicked.emit(self.metadata)

    def setSelected(self, isSelected: bool, force=False):
        if isSelected == self.isSelected and not force:
            return

        self.isSelected = isSelected

        if not isSelected:
            self.bookCover.set_pixmap(self.metadata["cover"])
        else:
            # HIGHLIGHT BOOK
            self.bookCover.set_pixmap(self.metadata["cover"])

        self.setProperty("isSelected", isSelected)
        self.setStyle(QApplication.style())
