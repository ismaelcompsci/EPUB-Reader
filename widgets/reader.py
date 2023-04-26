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

        self.button = SettingsOpenButton(FIF.MENU, "", True, self)

        # COMMENT FOR WEB DEBUG
        # self.vBoxLayout = QVBoxLayout(self)

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
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.book_view, 100)

        dev_view = QWebEngineView()
        self.mainLayout.addWidget(dev_view, 100)

        self.book_view.page().setDevToolsPage(dev_view.page())

        self.__initWidget()

    def __initWidget(self):
        self.resize(800, 720)
        self.setContentsMargins(0, 32, 0, 0)

        # self.vBoxLayout.addWidget(self.book_view)

        self.button.raise_()

        # PARSE BOOK FOR MISSING CONTENT
        self.book_view.load_book()

        # STYLE
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
            f"html {{background-color: {bg_color}; color: {color};}}"
        )

    def fontSizeChanged(self, size):
        self.book_view.document_js.setFontSize(size)

    def marginSizeChanged(self, size):
        self.book_view.document_js.setMargin(size)

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

    def closeEvent(self, event) -> None:
        self.book_view.save_book_data()

        return super().closeEvent(event)
