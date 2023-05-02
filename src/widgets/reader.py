from calendar import SATURDAY
from PyQt5 import QtGui
from config.config import EXTRACTED_EPUB_DIR, Books, cfg
from helpers.style_sheet import StyleSheet
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import Theme, isDarkTheme
from qframelesswindow import FramelessWindow, StandardTitleBar
from tinydb import Query

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

        self.button = SettingsOpenButton(FIF.MENU, "", True, self)

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
        self.dev_view = QWebEngineView()
        self.book_view.page().setDevToolsPage(self.dev_view.page())
        self.dev_view.show()

    def __initWidget(self):
        self.resize(640, 740)
        self.vBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.vBoxLayout.addWidget(self.book_view)
        # self.button.raise_()

        # STYLE
        StyleSheet.BOOK_WINDOW_INTERFACE.apply(self)
        self.book_view.setFocus()

    
    def themeChanged(self):
        # theme = Theme.DARK if isDarkTheme() else Theme.LIGHT
        # self.book_view.web_communicator.setTheme(theme.value)
        pass

    def fontSizeChanged(self, size):
        self.book_view.web_communicator.setFontSize_(size)
    
    def marginSizeChanged(self, size):
        ...

    def bookThemeChanged(self, theme):
        self.book_view.web_communicator.setBookTheme_(theme)


    def closeEvent(self, a0: QCloseEvent) -> None:
        # SAVE TO DATA BASE WHEN WINDOW IS CLOSING

        book_storage = self.book_view.web_communicator.book_storage

        self.metadata["currentCFI"] = book_storage["currentCFI"]
        self.metadata["sliderValue"]= book_storage["sliderValue"]
        self.metadata["settings"]= book_storage["settings"]
        self.metadata["progress"]= book_storage["progress"]

        SaveBook = Query()
        Books.update(book_storage, SaveBook.hash == self.metadata["hash"])
        return super().closeEvent(a0)