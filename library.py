import json
import PySide6
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *

from PySide6.QtWidgets import *
from qframelesswindow import *

from static import rc_resources

import os

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
            books.append(book)


class CustomWidget(QWidget):
    def __init__(self, text, img, parent=None):
        QWidget.__init__(self, parent)

        self._text = text
        self._img = img

        self.setLayout(QVBoxLayout())
        self.lbPixmap = QLabel(self)
        self.lbText = QLabel(self)
        self.lbText.setAlignment(Qt.AlignCenter)

        self.layout().addWidget(self.lbPixmap)
        self.layout().addWidget(self.lbText)

        self.initUi()

    def initUi(self):
        self.lbPixmap.setPixmap(
            QPixmap(self._img).scaled(
                self.lbPixmap.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding
            )
        )
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
        self.create_actions()
        self.create_tool_bar()

        layout = QVBoxLayout()

        self.table = QTableWidget()

        self.create_library()

        self.setLayout(layout)
        self.setCentralWidget(self.table)

    def create_library(self):

        images = get_image_from_database(os.path.join(temp, "db"))

        self.table.setRowCount(5)
        self.table.setColumnCount(5)

        # pass images into table
        for i in range(self.table.columnCount()):
            for j in range(self.table.rowCount()):
                lb = CustomWidget(
                    "imgae",
                    r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\temp\Old Man's War - John Scalzi.epub - cover",
                )
                self.table.setCellWidget(i, j, lb)

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
    mainwindow.show()
    app.exec()
