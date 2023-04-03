from PySide6.QtWidgets import *
from qframelesswindow import FramelessWindow, StandardTitleBar
from PySide6.QtGui import *
from PySide6.QtCore import *


class MyTitleBar(StandardTitleBar):
    def __init__(self, parent, cover):
        super().__init__(parent)

        self.toc_b = QPushButton("Contents")
        self.cover = cover

        self.settings_b = QPushButton()

        self.hBoxLayout.insertWidget(3, self.toc_b, 0, Qt.AlignmentFlag.AlignVCenter)
        self.setTitle(
            self.parent().content_view.this_book[self.parent().file_md5]["title"]
        )

        self.setStyleSheet(
            """
            QPushButton {
                background-color: transparent

                }
            QPushButton:hover {
            border: 1px solid black
            }
        """
        )
        self.addIconToButton()

    def addIconToButton(self):
        img = QImage.fromData(self.cover, "JPEG")
        self.q_img = QPixmap.fromImage(img)

        # RESIZE TO COVER IMAGE SIZE
        # size = self.q_img.size().toTuple()

        # self.parent().resize(size[0], size[1] + self.height() + 5)

        self.button_icon = QIcon(self.q_img)

        self.toc_b.setIcon(self.button_icon)
        self.toc_b.setIconSize(QSize(24, 24))
