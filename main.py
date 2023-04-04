import hashlib
import os
import sys

from components.book_view import EReader
from components.title_bar import MyTitleBar, SettingsWidget
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qframelesswindow import FramelessWindow

path_ = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\epubs\the_blade_itself.epub"
path_2 = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\epubs\Assassin's quest - Robin Hobb - Copy.epub"
path_3 = (
    r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\epubs\Old Man's War - John Scalzi.epub"
)
temp = r"C:\Users\Ismael\Documents\PROJECTS\EBookV2\temp"

with open(path_2, "rb") as current_book:
    first_bytes = current_book.read(1024 * 32)

file_md5 = hashlib.md5(first_bytes).hexdigest()


class EWindow(FramelessWindow):
    def __init__(self, filepath, temp, file_md5):
        super().__init__()

        self.filePath = filepath
        self.temp = temp
        self.file_md5 = file_md5

        self.set_layout()  # SET LAYOUT
        self.add_qss()

        # RESIZE GRIPS qwebengineview resize not working -> solution
        # https://stackoverflow.com/a/62812752
        self.gripSize = 14
        self.grips = []

        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            grip.setStyleSheet("""background-color: transparent""")
            self.grips.append(grip)

    # SET LAYOUT OF FRAMLESSWINDOW
    def set_layout(self) -> None:
        """
        Makes Ui layout and stuff
        """
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.content_view = EReader(self, self.filePath, self.temp, self.file_md5)
        self.content_view.load_book()
        self.content_view.set_content(0)

        self.layout_.addWidget(self.content_view)

        # SETTINGS TOGGLE
        self.settings_widget = SettingsWidget()
        # FONT SIZE
        self.settings_widget.font_size.valueChanged.connect(
            self.content_view.set_font_size
        )

        # BACKGROUND COLOR
        self.settings_widget.bg_dark.toggled.connect(
            lambda: self.content_view.bg_buttons_toggled(self.settings_widget.bg_dark)
        )
        self.settings_widget.bg_light.toggled.connect(
            lambda: self.content_view.bg_buttons_toggled(self.settings_widget.bg_light)
        )

        self.setLayout(self.layout_)

        self.setTitleBar(
            MyTitleBar(self, self.content_view.this_book[self.file_md5]["cover"])
        )
        self.titleBar.raise_()
        self.content_view.setFocus()

    def settings_button_clicked(self):
        """
        Hides or shows settings widget
        """
        if self.settings_widget.isHidden():
            self.settings_widget.show()
        else:
            self.settings_widget.hide()

        # self.layout_.addWidget(self.content_view)

    def add_qss(self):
        """
        add qss
        """
        qss = os.path.join(os.path.dirname(__file__), "static", "ewindow.qss")
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

    def next_chapter(self):
        self.content_view.change_chapter(1)

    def back_chapter(self):
        self.content_view.change_chapter(-1)

    def resizeEvent(self, event):
        """ADDS RESIZEABLE WINDOW EVENT"""
        super(EWindow, self).resizeEvent(event)
        rect = self.rect()
        # top left grip doesn't need to be moved...
        # top right
        self.grips[1].move(rect.right() - self.gripSize, 0)
        # bottom right
        self.grips[2].move(
            rect.right() - self.gripSize + 1, rect.bottom() + 1 - self.gripSize
        )
        # bottom left
        self.grips[3].move(0, rect.bottom() - self.gripSize + 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    mainwindow = EWindow(path_3, temp, file_md5)

    mainwindow.show()

    mainwindow.resize(500, 900)

    app.exec()
