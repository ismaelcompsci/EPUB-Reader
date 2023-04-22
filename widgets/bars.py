# coding:utf-8

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLabel, QVBoxLayout

from qframelesswindow import TitleBar

from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget, QFileDialog
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    PushButton,
    ToolButton,
    FluentIcon,
    Theme,
    SearchLineEdit,
    isDarkTheme,
    ToolTipFilter,
    NavigationItemPosition,
    NavigationToolButton,
    NavigationPanel,
)

from config.config import cfg


class LineEdit(SearchLineEdit):
    """Search line edit"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(self.tr("Search Books"))
        self.setFixedWidth(304)


class CustomTitleBar(TitleBar):
    """Title bar with icon and title"""

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(
            1,
            self.iconLabel,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        )
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(
            2,
            self.titleLabel,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
        )
        self.titleLabel.setObjectName("titleLabel")
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class LibraryToolBar(QWidget):
    """Tool bar"""

    openFileDialog = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.searchLine = LineEdit(self)
        self.addButton = PushButton("Add", self, FluentIcon.ADD)
        self.themeButton = ToolButton(FluentIcon.CONSTRACT, self)

        self.vBoxLayout = QVBoxLayout(self)
        self.buttonLayout = QHBoxLayout()

        self.__initWidget()

    def __initWidget(self):
        self.setFixedHeight(30)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.vBoxLayout.addLayout(self.buttonLayout, 1)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.buttonLayout.setSpacing(4)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.addWidget(self.searchLine, 0, Qt.AlignLeft)
        self.buttonLayout.addWidget(self.addButton, 0, Qt.AlignLeft)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.themeButton, 0, Qt.AlignRight)
        self.buttonLayout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        self.themeButton.installEventFilter(ToolTipFilter(self.themeButton))
        self.themeButton.setToolTip(self.tr("Toggle theme"))

        self.themeButton.clicked.connect(self.toggleTheme)
        self.addButton.clicked.connect(self.openFileDialog.emit)

        self.searchLine.textChanged.connect(self.parent().search)

    def toggleTheme(self):
        theme = Theme.LIGHT if isDarkTheme() else Theme.DARK
        cfg.set(cfg.themeMode, theme)
