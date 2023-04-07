import base64
import json
import os

import PySide6
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import *
from main_reader_view import EWindow
from qframelesswindow import *


from static import rc_resources

basedir = os.path.dirname(__file__)

temp = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\temp"


def get_image_from_database(db_path):
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


class CustomWidget(QWidget):
    def __init__(self, metadata, parent=None):
        QWidget.__init__(self, parent)

        self.file_md5 = metadata["hash"]
        self.full_metadata = metadata["book"]

        self._text = self.full_metadata[self.file_md5]["title"]

        self.cover = base64.b64decode(self.full_metadata[self.file_md5]["cover"])
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.cover)

        self.setLayout(QVBoxLayout())
        self.lbPixmap = QLabel(self)
        self.lbText = QLabel(self)
        self.lbText.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.layout().addWidget(self.lbPixmap)
        self.layout().addWidget(self.lbText)

        self.initUi()

    def initUi(self):

        pix = self.pixmap.scaled(
            100, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )

        self.lbPixmap.setPixmap(pix)

        self.lbText.setText(self._text)

    def img(self):
        return self._img

    def total(self, value):
        if self._img == value:
            return
        self._img = value
        self.initUi()

    def text(self):
        return self._text

    def text(self, value):
        if self._text == value:
            return
        self._text = value
        self.initUi()

    # def mouseDoubleClickEvent(self, event: PySide6.QtGui.QMouseEvent) -> None:

    #     return super().mouseDoubleClickEvent(event)


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

        images = get_image_from_database(os.path.join(temp, "db"))

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

    def book_selected(self, row, column):
        book = self.cellWidget(row, column)

        file_md5 = book.file_md5
        filepath = book.full_metadata[file_md5]["path"]

        temp_ = temp

        ewindow = EWindow(filepath, temp_, file_md5, book.full_metadata)
        ewindow.show()


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()

        self.resize(800, 600)

        self.v_layout = QVBoxLayout()

        self.table = Library(self)

        self.v_layout.addWidget(self.table)

        self.add_book = QPushButton("Add Book")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.setStyleSheet("background-color: white")
    mainwindow.show()
    app.exec()
