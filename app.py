import os

import PySide6
from components.book_view import BookHandler
from components.custom_widgets import CustomWidget
from main_reader_view import EWindow
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWidgets import *
from qframelesswindow import *
from static import rc_resources
from utils.utils import get_image_from_database

BASEDIR = os.path.dirname(__file__)

TEMPDIR = os.path.join(BASEDIR, "temp")

if not os.path.exists(TEMPDIR):
    os.makedirs(TEMPDIR)

# TODO
# LOOK AT FRAMELESSWINDOW EVENTFILTER

# TODO
# SET TYPES


# TODO
# PUT NEW CLASSES IN SEPERATE FILES
# IMPLEMENT ADD BOOK BUTTON
# ON BOOK CLICK OPEN WINDOW AT LAST LOCATION AND SIZE
#     - 1ST OPEN AT LAST CHAPTER
#     - 2ND SCROLL TO LAST POSITION


class Library(QTableWidget):
    """
    Table view for books
    """

    def __init__(self, parent: QWidget) -> None:
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

    def create_library(self) -> None:
        """
        Populate table widget
        """

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

    def book_selected(self, row: int, column: int) -> None:
        """
        Open selected book
        """
        book = self.cellWidget(row, column)

        file_md5 = book.file_md5
        filepath = book.full_metadata[file_md5]["path"]

        temp_ = TEMPDIR

        ewindow = EWindow(filepath, temp_, file_md5, book.full_metadata)

        ewindow.show()

    def book_added(self, file: str) -> None:
        """
        Adds book the database and reloads table widget
        """
        handle = BookHandler(file, temp_dir=TEMPDIR)
        handle.save_book()

        self.clear()
        self.create_library()


class MainWindow(FramelessWindow):
    """
    Main view for app
    """

    def __init__(self) -> None:
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

    def add_book_clicked(self) -> None:
        """
        Opens book
        """
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
