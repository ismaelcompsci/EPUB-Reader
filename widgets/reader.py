from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qframelesswindow import FramelessWindow, StandardTitleBar, TitleBar
from tinydb import TinyDB

from .book_view import BookViewer
from config.config import EXTRACTED_EPUB_DIR, DATABASE_DIR, Books, cfg
from helpers.style_sheet import StyleSheet

from qfluentwidgets import (
    ScrollArea,
    FluentStyleSheet,
    PrimaryPushButton,
    isDarkTheme,
    themeColor,
    FluentIcon as FIF,
    drawIcon,
    NavigationPushButton,
    Theme,
    SpinBox,
)

from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase
from qfluentwidgets.components.dialog_box.color_dialog import BrightnessSlider


class SettingsCard(MaskDialogBase):
    settingsChanged = pyqtSignal(dict)

    def __init__(self, settings, parent=None):
        super().__init__(parent)

        self.oldBookSettings = settings
        self.bookSettings = settings

        self.scrollArea = ScrollArea(self.widget)
        self.scrollWidget = QWidget(self.scrollArea)

        self.buttonGroup = QFrame(self.widget)
        self.yesButton = PrimaryPushButton(self.tr("OK"), self.buttonGroup)
        self.cancelButton = QPushButton(self.tr("Cancel"), self.buttonGroup)

        self.titleLabel = QLabel("Book Setttings", self.scrollWidget)

        self.fontSizeBox = SpinBox(self.scrollWidget)

        self.vBoxLayout = QVBoxLayout(self.widget)

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setViewportMargins(48, 24, 0, 24)
        self.scrollArea.setWidget(self.scrollWidget)

        self.widget.setMaximumSize(488, 696)
        self.widget.resize(424, 646)
        self.scrollWidget.resize(440, 560)
        self.buttonGroup.setFixedSize(486, 81)
        self.yesButton.setFixedWidth(216)
        self.cancelButton.setFixedWidth(216)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 80))
        self.setMaskColor(QColor(0, 0, 0, 76))

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.fontSizeBox.move(0, 324)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)

        self.yesButton.move(24, 25)
        self.cancelButton.move(250, 25)

    def __setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.yesButton.setObjectName("yesButton")
        self.cancelButton.setObjectName("cancelButton")
        self.buttonGroup.setObjectName("buttonGroup")
        self.fontSizeBox.setObjectName("fontSizeSpinBox")
        FluentStyleSheet.COLOR_DIALOG.apply(self)
        self.titleLabel.adjustSize()
        self.fontSizeBox.adjustSize()

    def updateStyle(self):
        """update style sheet"""
        self.setStyle(QApplication.style())
        self.titleLabel.adjustSize()
        self.fontSizeBox.adjustSize()

    def __onYesButtonClicked(self):
        self.accept()

        self.settingsChanged.emit(self.bookSettings)

    def __connectSignalToSlot(self):
        self.cancelButton.clicked.connect(self.reject)
        self.yesButton.clicked.connect(self.__onYesButtonClicked)

        self.fontSizeBox.valueChanged.connect(lambda v: print(v))


class SettingsOpenButton(NavigationPushButton):
    def __init__(self, icon, text: str, isSelectable: bool, parent=None):
        super().__init__(icon, text, isSelectable, parent)
        self.icon = icon
        self._text = "WHaT"

        self.setStyleSheet(
            "NavigationPushButton{font: 14px 'Segoe UI', 'Microsoft YaHei'}"
        )

    def text(self):
        return self._text

    def mousePressEvent(self, e):
        w = SettingsCard({}, self.window())
        w.updateStyle()
        w.exec()
        return super().mousePressEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)
        if not self.isEnabled():
            painter.setOpacity(0.4)

        # draw background
        c = 255 if isDarkTheme() else 0
        if self.isSelected:
            painter.setBrush(QColor(c, c, c, 6 if self.isEnter else 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

            # draw indicator
            painter.setBrush(themeColor())
            painter.drawRoundedRect(0, 10, 3, 16, 1.5, 1.5)
        elif self.isEnter and self.isEnabled():
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        drawIcon(self.icon, painter, QRectF(11.5, 10, 16, 16))


class ReaderInterfaceWindow(FramelessWindow):
    def __init__(self, metadata):
        super().__init__()
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()

        self.button = SettingsOpenButton(FIF.MENU, "WHAT", True, self)

        self.metadata = metadata
        self.book_view = BookViewer(
            self,
            self.metadata["path"],
            EXTRACTED_EPUB_DIR,
            self.metadata["hash"],
            Books,
            self.metadata,
        )
        self.book_view.load_book()

        self.__initWidget()

    def __initWidget(self):
        self.resize(800, 720)
        self.setContentsMargins(0, 32, 0, 0)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.book_view)
        self.button.raise_()

        StyleSheet.BOOK_WINDOW_INTERFACE.apply(self)

        cfg.themeChanged.connect(self.__themeColorChanged)

        self.__themeColorChanged(Theme.DARK if isDarkTheme() else Theme.LIGHT)

    def __themeColorChanged(self, theme):
        if theme == Theme.DARK:
            bg_color = "rgb(39, 39, 39)"
            color = "rgb(249, 249, 249)"
        if theme == Theme.LIGHT:
            bg_color = "rgb(255, 255, 255)"
            color = "black"

        self.book_view.insert_web_view_css(
            f"*{{background-color: {bg_color}; color: {color};}}"
        )

    def keyPressEvent(self, ev: QKeyEvent) -> None:
        """
        Keyboard arrows to change page
        """

        key = ev.key()

        if key == Qt.Key.Key_Right:
            self.book_view.change_chapter(1)
        if key == Qt.Key.Key_Left:
            self.book_view.change_chapter(-1, True)

    def resizeEvent(self, e):
        self.button.move(self.width() - 50, 38)
        return super().resizeEvent(e)


# class BookTitleBar(TitleBar):
#     def __init__(self, parent):
#         super().__init__(parent)

#         self.iconLabel = QLabel(self)
#         self.iconLabel.setFixedSize(18, 18)
#         self.hBoxLayout.insertSpacing(0, 10)
#         self.hBoxLayout.insertWidget(
#             1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignBottom
#         )
#         self.window().windowIconChanged.connect(self.setIcon)

#         # add title label
#         self.titleLabel = QLabel(self)
#         self.hBoxLayout.insertWidget(
#             2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignBottom
#         )
#         self.titleLabel.setObjectName("titleLabel")
#         self.window().windowTitleChanged.connect(self.setTitle)

#     def setTitle(self, title):
#         self.titleLabel.setText(title)
#         self.titleLabel.adjustSize()

#     def setIcon(self, icon):
#         self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))
