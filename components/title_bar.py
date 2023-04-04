from json import tool
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QSpinBox,
    QFrame,
    QRadioButton,
)

from qframelesswindow import StandardTitleBar, FramelessWindow

# CREATE SETTINGS WIDGET
# CHANGE FONT SIZE
# CHANGE FONT FAMILY
# CHANGE BACKGROUND COLOR LIGHT OR DARK


class SettingsWidget(FramelessWindow):
    def __init__(self):
        super().__init__()

        # WIDGET LAYOUT
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        layout.setContentsMargins(10, self.titleBar.height(), 10, 10)

        h_layout = QHBoxLayout()

        # HANDLE FONT SIZE
        self.font_label = QLabel("Font Size:")
        self.font_size = QSpinBox()
        self.font_size.setValue(16)
        self.font_size.setMinimum(16)
        h_layout.addWidget(self.font_label)
        h_layout.addWidget(self.font_size)
        layout.addLayout(h_layout)

        # SEPARATOR LINE
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFrameShadow(QFrame.Shadow.Raised)

        layout.addWidget(self.separator)

        # BACKGROUND COLOR
        self.bg_dark = QRadioButton("Dark")
        self.bg_light = QRadioButton("Light")

        self.bg_light.setChecked(True)

        layout.addWidget(self.bg_dark)
        layout.addWidget(self.bg_light)

        self.setLayout(layout)
        self.titleBar.raise_()
        self.resize(300, 150)


class MyTitleBar(StandardTitleBar):
    def __init__(self, parent, cover):
        super().__init__(parent)

        self.toc_b = QPushButton("Contents")
        self.cover = cover

        self.settings_b = QPushButton("Settings")
        self.settings_b.clicked.connect(self.parent().settings_button_clicked)

        self.hBoxLayout.insertWidget(3, self.toc_b, 0, Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.insertWidget(
            5, self.settings_b, 0, Qt.AlignmentFlag.AlignVCenter
        )
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
