from config.config import cfg
from typing import Union
from PyQt5.QtGui import QIcon
from helpers.style_sheet import StyleSheet
from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import ComboBox, ExpandLayout
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
    SingleDirectionScrollArea,
    ExpandLayout,
    ComboBox,
    SettingCard,
    FluentIconBase,
)
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase

BOOK_THEMES = {
    "0": "Light",
    "1": "Dark",
    "2": "Hacker",
    "3": "Owl",
    "4": "Tan",
}
BOOK_THEMES_R = {
    "light": "0",
    "dark": "1",
    "hacker": "2",
    "owl": "3",
    "tan": "4",
}


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


# ----------------------------------------------


class SettingPopUpDialog(MaskDialogBase):
    def __init__(self, parent=None, title: str = None):
        super().__init__(parent)

        self.buttonGroup = QFrame(self.widget)

        self.scrollArea = SingleDirectionScrollArea(self.widget)
        self.scrollWidget = QWidget(self.scrollArea)

        self.yesButton = PrimaryPushButton(self.tr("OK"), self.buttonGroup)
        self.cancelButton = QPushButton(self.tr("Cancel"), self.buttonGroup)

        self.vBoxLayout = QVBoxLayout(self.widget)

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.scrollArea.setViewportMargins(48, 24, 0, 24)
        self.scrollArea.setWidget(self.scrollWidget)

        self.widget.setMaximumSize(488, 696 + 40)
        self.widget.resize(488, 696 + 40)
        self.scrollWidget.resize(440, 560 + 40)
        self.buttonGroup.setFixedSize(486, 81)
        self.yesButton.setFixedWidth(216)
        self.cancelButton.setFixedWidth(216)
        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 80))
        self.setMaskColor(QColor(0, 0, 0, 76))

        self.__setQss()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)

        self.yesButton.move(24, 25)
        self.cancelButton.move(250, 25)

    def __setQss(self):
        self.yesButton.setObjectName("yesButton")
        self.cancelButton.setObjectName("cancelButton")
        self.buttonGroup.setObjectName("buttonGroup")
        FluentStyleSheet.COLOR_DIALOG.apply(self)

    def __onYesButtonClicked(self):
        """yes button clicked slot"""
        self.accept()
        # WHEN CLICKED SAVE SETTINGS TO DICT

    def updateStyle(self):
        """update style sheet"""
        self.setStyle(QApplication.style())

    def showEvent(self, e):
        self.updateStyle()
        super().showEvent(e)

    def __connectSignalToSlot(self):
        self.cancelButton.clicked.connect(self.reject)
        self.yesButton.clicked.connect(self.__onYesButtonClicked)


class CustomComboBoxSettingCard(SettingCard):
    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title,
        content=None,
        texts=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)

        self.comboBox = ComboBox(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.texts = texts
        for text in self.texts:
            self.comboBox.addItem(text)

    def setValue(self, value):
        if value not in self.texts:
            return

        self.comboBox.setCurrentText(value)


class CustomSettingsDialog(SettingPopUpDialog):
    bookThemeChanged = pyqtSignal(str)
    bookFontSizeChanged = pyqtSignal(str)
    bookMarginSizechaned = pyqtSignal(str)

    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent, "Settings")
        # ADD EVERY THING TO SCROLL WIDGTE
        # self.huePanel = HuePanel(color, self.scrollWidget)
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.themesGroup = SettingCardGroup("Book Themes", self.scrollWidget)

        self.themeCard = CustomComboBoxSettingCard(
            icon=FIF.PALETTE,
            title="Book Themes",
            content="Change the current book theme",
            texts=[BOOK_THEMES[str(i)] for i in range(len(BOOK_THEMES))],
            parent=self.themesGroup,
        )
        self.themeCard.setValue(theme.capitalize())

        self.themesGroup.addSettingCard(self.themeCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 0, 0)
        self.expandLayout.addWidget(self.themesGroup)

        self.themeCard.comboBox.currentTextChanged.connect(self.handleBookThemeChanged)

    def handleBookThemeChanged(self, theme):
        self.bookThemeChanged.emit(theme.lower())

    def handleFontSizeChanged(self, size):
        ...

    def handleMarginSizeChanged(self, size):
        ...


class SettingsOpenButton(NavigationPushButton):
    bookThemeChangedSignal = pyqtSignal(str)
    bookMarginChangedSignal = pyqtSignal(str)

    def __init__(
        self, icon, text: str, isSelectable: bool, parent=None, currentTheme=None
    ):
        super().__init__(icon, text, isSelectable, parent)
        self.icon = icon
        self._text = ""
        self.currentTheme = currentTheme

        self.setStyleSheet(
            "NavigationPushButton{font: 14px 'Segoe UI', 'Microsoft YaHei'}"
        )

    def text(self):
        return self._text

    def mousePressEvent(self, e):
        w = CustomSettingsDialog(self.window(), self.currentTheme)
        w.themeCard.comboBox.currentTextChanged.connect(self._changeTheme_)
        w.bookThemeChanged.connect(self.bookThemeChanged_)
        w.bookMarginSizechaned.connect(self.marginSizeChanged_)
        w.exec()

    def _changeTheme_(self, theme):
        self.currentTheme = theme

    def bookThemeChanged_(self, theme):
        self.bookThemeChangedSignal.emit(theme)

    def marginSizeChanged_(self, size):
        self.bookMarginChangedSignal.emit(size)

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
