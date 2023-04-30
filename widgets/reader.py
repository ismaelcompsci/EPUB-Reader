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
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()

        self.metadata = metadata

        # self.button = SettingsOpenButton(FIF.MENU, "", True, self)

        # COMMENT FOR WEB DEBUG
        self.vBoxLayout = QVBoxLayout(self)

        # WEB ENGINE
        self.book_view = BookViewer(
            self,
            self.metadata["path"],
            EXTRACTED_EPUB_DIR,
            self.metadata["hash"],
            Books,
            self.metadata,
        )

        # DEBUGGING WEB
        # self.mainLayout = QHBoxLayout(self)
        # self.mainLayout.addWidget(self.book_view, 100)

        # dev_view = QWebEngineView()
        # self.mainLayout.addWidget(dev_view, 100)

        # self.book_view.page().setDevToolsPage(dev_view.page())

        self.__initWidget()

    def __initWidget(self):
        self.resize(550, 700)
        self.setContentsMargins(0, 20, 0, 0)

        self.vBoxLayout.addWidget(self.book_view)

        # self.button.raise_()

        # STYLE
        StyleSheet.BOOK_WINDOW_INTERFACE.apply(self)
