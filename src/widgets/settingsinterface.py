from re import S
import typing

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget
from config.config import cfg
from helpers.style_sheet import StyleSheet
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import ExpandLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentStyleSheet,
    InfoBar,
    NavigationPushButton,
    OptionsSettingCard,
    PrimaryPushButton,
    ScrollArea,
    SettingCardGroup,
    SpinBox,
    drawIcon,
    isDarkTheme,
    setTheme,
    themeColor,
    ComboBox
)
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase


class SettingInterface(ScrollArea):
    checkUpdateSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel("Settings", self)

        # Personilazation Group
        self.personalGroup = SettingCardGroup("Personalization", self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            "Application Theme",
            "Change the appearance of your application",
            texts=["Light", "Dark"],
            parent=self.personalGroup,
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        self.scrollWidget.setObjectName("scrollWidget")
        self.settingLabel.setObjectName("settingLabel")

        # Set stylesheet
        StyleSheet.SETTING_INTERFACE.apply(self)

        # initalize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        self.personalGroup.addSettingCard(self.themeCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)

    def __connectSignalToSlot(self):
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(setTheme)

    def __showRestartTooltip(self):
        InfoBar.success(
            "Updated Successfully",
            "Configuration takes effect after restart",
            duration=1500,
            parent=self,
        )


# BOOK WINDOW SETTINGS
class SettingsCard(MaskDialogBase):
    fontSizeChanged = pyqtSignal(int)
    marginSizeChanged = pyqtSignal(int)
    bookThemeChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mainwindow = parent

        self.scrollArea = ScrollArea(self.widget)
        self.scrollWidget = QWidget(self.scrollArea)

        self.buttonGroup = QFrame(self.widget)
        self.yesButton = PrimaryPushButton("OK", self.buttonGroup)
        self.cancelButton = QPushButton("Cancel", self.buttonGroup)

        self.titleLabel = QLabel("Book Settings", self.scrollWidget)
        self.themepicker = ComboBox(self.scrollWidget)

        self.editLabel = QLabel("Edit Page", self.scrollWidget)

        self.fontSizeLabel = QLabel("Font Size", self.scrollWidget)
        self.marginSizeLabel = QLabel("Margin Size", self.scrollWidget)

        self.fontSizeBox = SpinBox(self.scrollWidget)
        self.fontSizeBox.setValue(int(self.mainwindow.metadata["settings"]["fontSize"]))

        self.marginSizeBox = SpinBox(self.scrollWidget)
        self.marginSizeBox.setValue(int(self.mainwindow.metadata["settings"]["margin"]))


        self.themepicker.addItems(["dark", "light", "hacker", "tan", "owl"])
        self.themepicker.setCurrentText(self.mainwindow.metadata["settings"]["theme"])
        self.themepicker.currentTextChanged.connect(self.onBookThemeChanged)

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
        self.themepicker.move(0, 46)

        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)

        self.editLabel.move(0, 381)

        self.fontSizeLabel.move(144, 434)
        self.marginSizeLabel.move(144, 478)

        self.fontSizeBox.move(0, 426)
        self.marginSizeBox.move(0, 470)

        self.yesButton.move(24, 25)
        self.cancelButton.move(250, 25)

    def __setQss(self):
        self.editLabel.setObjectName("editLabel")
        self.titleLabel.setObjectName("titleLabel")
        self.yesButton.setObjectName("yesButton")
        self.cancelButton.setObjectName("cancelButton")
        self.buttonGroup.setObjectName("buttonGroup")
        self.fontSizeBox.setObjectName("fontSizeSpinBox")
        FluentStyleSheet.COLOR_DIALOG.apply(self)
        self.titleLabel.adjustSize()
        # self.fontSizeBox.adjustSize()
        # self.editLabel.adjustSize()

    def updateStyle(self):
        """update style sheet"""
        self.setStyle(QApplication.style())
        self.titleLabel.adjustSize()
        self.fontSizeBox.adjustSize()

    def __onYesButtonClicked(self):
        self.accept()
        cfg.save()

    def onFontSizeChanged(self, size):
        self.mainwindow.metadata["settings"]["fontSize"] = size
        self.fontSizeChanged.emit(size)

    def onMarginSizeChanged(self, size):
        self.mainwindow.metadata["settings"]["margin"]= size
        self.marginSizeChanged.emit(size)

    def onBookThemeChanged(self, text):
        self.mainwindow.metadata["settings"]["theme"]= text
        self.bookThemeChanged.emit(text)

    def __connectSignalToSlot(self):
        self.cancelButton.clicked.connect(self.reject)
        self.yesButton.clicked.connect(self.__onYesButtonClicked)

        self.fontSizeBox.valueChanged.connect(self.onFontSizeChanged)
        self.marginSizeBox.valueChanged.connect(self.onMarginSizeChanged)


class SettingsOpenButton(NavigationPushButton):
    def __init__(self, icon, text: str, isSelectable: bool, parent=None):
        super().__init__(icon, text, isSelectable, parent)
        self.icon = icon
        self._text = ""

        self.setStyleSheet(
            "NavigationPushButton{font: 14px 'Segoe UI', 'Microsoft YaHei'}"
        )

    def text(self):
        return self._text

    def mousePressEvent(self, e):
        w = SettingsCard(self.window())
        w.updateStyle()
        w.fontSizeChanged.connect(lambda size: self.parent().fontSizeChanged(size))
        w.marginSizeChanged.connect(lambda size: self.parent().marginSizeChanged(size))
        w.bookThemeChanged.connect(lambda theme: self.parent().bookThemeChanged(theme))
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
