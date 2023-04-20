from qfluentwidgets import (
    SettingCardGroup,
    SwitchSettingCard,
    FolderListSettingCard,
    OptionsSettingCard,
    PushSettingCard,
    HyperlinkCard,
    PrimaryPushSettingCard,
    ScrollArea,
    ComboBoxSettingCard,
    ExpandLayout,
    Theme,
    CustomColorSettingCard,
    setTheme,
    setThemeColor,
    RangeSettingCard,
    isDarkTheme,
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog
from config.config import cfg
from helpers.style_sheet import StyleSheet


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
