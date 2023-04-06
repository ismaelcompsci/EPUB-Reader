import base64
import json
import os

import PySide6
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import *
from qframelesswindow import *
from static import rc_resources

basedir = os.path.dirname(__file__)

temp = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\temp"

# TODO
# return qpixmap form book[file_md5]["cover"] -> decode from bs64
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
        self.metadata = metadata["book"][self.file_md5]

        self._text = self.metadata["title"]

        self.cover = base64.b64decode(self.metadata["cover"])
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)

        self.H_layout = QVBoxLayout()

        self.create_actions()
        self.create_tool_bar()

        self.table = QTableWidget()
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setShowGrid(False)
        self.table.horizontalHeader().hide()
        self.table.verticalHeader().hide()

        # self.table.horizontalHeader().setSectionResizeMode(
        #     QHeaderView.ResizeMode.Stretch
        # )

        self.create_library()

        self.setLayout(self.H_layout)
        self.setCentralWidget(self.table)

    def create_library(self):

        images = get_image_from_database(os.path.join(temp, "db"))

        self.table.setRowCount(len(images))
        self.table.setColumnCount(5)

        # pass images into table
        try:
            for i in range(self.table.rowCount()):
                for j in range(self.table.columnCount()):

                    lb = CustomWidget(
                        images[i][j],
                    )
                    self.table.setCellWidget(i, j, lb)
        except IndexError:
            pass

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def create_actions(self):
        self.new_action = QAction(self)
        self.new_action.setText("Add Book")
        self.new_action.setIcon(QIcon(":add.png"))

    def create_tool_bar(self):
        add_book_bar = self.addToolBar("Add Book")
        add_book_bar.addAction(self.new_action)
        add_book_bar.setMovable(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    # mainwindow.setStyleSheet("")
    mainwindow.show()
    app.exec()
