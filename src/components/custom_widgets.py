import base64
import logging
import qdarkstyle
from PySide6.QtCore import QSize, Qt, QFile, QTextStream
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from qframelesswindow import FramelessWindow, StandardTitleBar

# CREATE SETTINGS WIDGET
# CHANGE FONT SIZE
# CHANGE FONT FAMILY
# CHANGE BACKGROUND COLOR LIGHT OR DARK

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class SettingsWidget(FramelessWindow):
    """
    Settings widget
    """

    def __init__(self) -> None:
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
        # self.bg_dark = QRadioButton("Dark")
        # self.bg_light = QRadioButton("Light")

        # self.bg_light.setChecked(True)

        # layout.addWidget(self.bg_dark)
        # layout.addWidget(self.bg_light)

        self.setLayout(layout)
        self.titleBar.raise_()
        self.resize(300, 150)


class MyTitleBar(StandardTitleBar):
    def __init__(self, parent: QWidget, cover: bytes) -> None:
        super().__init__(parent)
        self.toc_b = QPushButton("Contents")
        self.cover = cover

        self.settings_b = QPushButton("Settings")
        self.settings_b.clicked.connect(self.parent().settings_button_clicked)

        self.hBoxLayout.insertWidget(3, self.toc_b, 0, Qt.AlignmentFlag.AlignVCenter)
        self.hBoxLayout.insertWidget(
            5, self.settings_b, 0, Qt.AlignmentFlag.AlignVCenter
        )
        self.setTitle(self.parent().content_view.this_book["title"])

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

    def addIconToButton(self) -> None:
        img = QImage.fromData(self.cover, "JPEG")
        self.q_img = QPixmap.fromImage(img)

        # RESIZE TO COVER IMAGE SIZE
        # size = self.q_img.size().toTuple()

        # self.parent().resize(size[0], size[1] + self.height() + 5)

        self.button_icon = QIcon(self.q_img)

        self.toc_b.setIcon(self.button_icon)
        self.toc_b.setIconSize(QSize(24, 24))


class CustomWidget(QWidget):
    def __init__(self, metadata: dict, parent: QWidget = None):
        QWidget.__init__(self, parent)

        self.file_md5 = metadata["hash"]
        self.full_metadata = metadata

        self._text = self.full_metadata["title"]

        self.cover = base64.b64decode(self.full_metadata["cover"])
        self.pixmap = QPixmap()
        self.pixmap.loadFromData(self.cover)

        self.setLayout(QVBoxLayout())
        self.lbPixmap = QLabel(self)
        self.lbText = QLabel(self)
        self.lbText.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lbText.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

        self.layout().addWidget(self.lbPixmap)
        self.layout().addWidget(self.lbText)

        self.initUi()

    def initUi(self):
        """
        Set image into qlabel
        """

        pix = self.pixmap.scaled(
            100, 200, Qt.AspectRatioMode.KeepAspectRatioByExpanding
        )

        self.lbPixmap.setPixmap(pix)
        if isinstance(self._text, dict):
            logger.info(f'Trying to find title in: {self.full_metadata["path"]}')

            try:
                self._text = self._text["#text"]
            except:
                logger.warning(f'Title not found in: {self.full_metadata["path"]}')

                self._text = ""

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
