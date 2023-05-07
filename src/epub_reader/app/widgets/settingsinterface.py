from typing import Union

from epub_reader.app.utils.style_sheet import StyleSheet
from epub_reader.config.config import BOOK_THEMES, cfg
from PyQt5.QtCore import QRectF, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QPainter
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import ComboBox, ExpandLayout
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    FluentIconBase,
    FluentStyleSheet,
    InfoBar,
    NavigationPushButton,
    OptionsSettingCard,
    PrimaryPushButton,
    ScrollArea,
    SettingCard,
    SettingCardGroup,
    SingleDirectionScrollArea,
    drawIcon,
    isDarkTheme,
    setTheme,
    themeColor,
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


# https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/c8fb1eb1140ede339c7ab9091ca2b5eac4c43e7a/qfluentwidgets/components/settings/setting_card.py#L365
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


# https://github.com/zhiyiYo/PyQt-Fluent-Widgets/blob/c8fb1eb1140ede339c7ab9091ca2b5eac4c43e7a/qfluentwidgets/components/settings/setting_card.py#L144
class CustomRangeSettingCard(SettingCard):
    valueChanged = pyqtSignal(int)

    def __init__(
        self,
        icon: Union[str, QIcon, FluentIconBase],
        title,
        content=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.slider = QSlider(Qt.Horizontal, self)
        self.valueLabel = QLabel(self)
        self.slider.setFixedSize(150, 24)

        self.slider.setSingleStep(1)
        self.slider.setRange(0, 100)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.valueLabel, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(6)
        self.hBoxLayout.addWidget(self.slider, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.valueLabel.setObjectName("valueLabel")
        self.slider.valueChanged.connect(self.__onValueChanged)

    def __onValueChanged(self, value: int):
        """slider value changed slot"""
        self.setValue(value)
        self.valueChanged.emit(value)

    def setValue(self, value):
        self.valueLabel.setNum(value)
        self.valueLabel.adjustSize()


class CustomSettingsDialog(SettingPopUpDialog):
    def __init__(self, parent=None, theme="dark"):
        super().__init__(parent, "Settings")
        self.setStyleSheet(" ")
        self.reader_window = parent
        self._theme = theme
        # ADD EVERY THING TO SCROLL WIDGTE
        # self.huePanel = HuePanel(color, self.scrollWidget)
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.themesGroup = SettingCardGroup("Book Themes", self.scrollWidget)
        self.textGroup = SettingCardGroup("Text", self.scrollWidget)

        self.themeCard = CustomComboBoxSettingCard(
            icon=FIF.PALETTE,
            title="Book Themes",
            content="Change the current book theme",
            texts=[theme for theme in BOOK_THEMES],
            parent=self.themesGroup,
        )

        self.fontSizeCard = CustomRangeSettingCard(
            icon=FIF.ALIGNMENT,
            title="Font Size",
            content="Change font size",
            parent=self.textGroup,
        )

        self.themeCard.comboBox.currentTextChanged.connect(self.handleBookThemeChanged)
        self.fontSizeCard.valueChanged.connect(self.handleFontSizeChanged)

        StyleSheet.DIALOG_INTERFACE.apply(self)

        self.__initDialog()

    def __initDialog(self):
        self.themeCard.setValue(
            self.reader_window.metadata["settings"]["theme"].capitalize()
        )
        self.fontSizeCard.setValue(self.reader_window.metadata["settings"]["margin"])
        self.fontSizeCard.slider.setValue(
            self.reader_window.metadata["settings"]["margin"]
        )

        self.themesGroup.addSettingCard(self.themeCard)
        self.textGroup.addSettingCard(self.fontSizeCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 0, 0)
        self.expandLayout.addWidget(self.themesGroup)
        self.expandLayout.addWidget(self.textGroup)

    def handleBookThemeChanged(self, theme):
        self.reader_window.bookThemeChanged(theme.lower())

    def handleFontSizeChanged(self, size):
        self.reader_window.fontSizeChanged(size)

    # def handleMarginSizeChanged(self, size):
    #     self.reader_window.marginSizeChanged(size)


class SettingsOpenButton(NavigationPushButton):
    def __init__(
        self, icon, text: str, isSelectable: bool, parent=None, metadata: dict = None
    ):
        super().__init__(icon, text, isSelectable, parent)
        self.icon = icon
        self._text = ""
        self.metadata = metadata

        self.setStyleSheet(
            "NavigationPushButton{font: 14px 'Segoe UI', 'Microsoft YaHei'}"
        )

    def text(self):
        return self._text

    def mousePressEvent(self, e):
        w = CustomSettingsDialog(self.window())
        w.themeCard.comboBox.currentTextChanged.connect(self._changeTheme_)
        w.exec()

    def _changeTheme_(self, theme):
        self.currentTheme = theme

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
