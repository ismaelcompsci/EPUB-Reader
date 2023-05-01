from PyQt5 import QtGui
from config.config import EXTRACTED_EPUB_DIR, Books, cfg
from helpers.style_sheet import StyleSheet
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import Theme, isDarkTheme
from qframelesswindow import FramelessWindow, StandardTitleBar
from tinydb import TinyDB

from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from .book_view import BookViewer
from .settingsinterface import SettingsOpenButton


class ReaderInterfaceWindow(FramelessWindow):

    def __init__(self, metadata):
        super().__init__()
        # COMMENT FOR WEB DEBUG
        self.vBoxLayout = QVBoxLayout(self)

        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()

        self.metadata = metadata

        # self.button = SettingsOpenButton(FIF.MENU, "", True, self)

        # WEB ENGINE
        self.book_view = BookViewer(
            self,
            self.metadata["path"],
            EXTRACTED_EPUB_DIR,
            self.metadata["hash"],
            Books,
            self.metadata,
        )

        self.__initWidget()

        # DEBUGGING WEB
        # UNCOMMENT FOR WEB DEBBUGING
        # self.dev_view = QWebEngineView()
        # self.book_view.page().setDevToolsPage(self.dev_view.page())
        # self.dev_view.show()

    def __initWidget(self):
        self.resize(550, 700)
        self.vBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.vBoxLayout.addWidget(self.book_view)
        # self.button.raise_()

        # STYLE
        StyleSheet.BOOK_WINDOW_INTERFACE.apply(self)
        self.book_view.setFocus()

    
    def themeChanged(self):
        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT
        self.book_view.web_communicator.setTheme(theme.value)


    # def keyPressEvent(self, a0: QKeyEvent) -> None:
    #     key = a0.key()

    #     if key == Qt.Key.Key_Right:
    #         self.book_view.web_communicator.chapterChangedEvent("next")
    #     elif key == Qt.Key.Key_Left:
    #         self.book_view.web_communicator.chapterChangedEvent("prev")

