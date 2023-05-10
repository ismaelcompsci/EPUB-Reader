from epub_reader.app.utils.style_sheet import StyleSheet
from epub_reader.app.widgets.book_view import BookViewer
from epub_reader.app.widgets.settingsinterface import SettingsOpenButton
from epub_reader.config.config import EXTRACTED_EPUB_DIR, Books
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar
from tinydb import Query

import ctypes
import win32con
import sys


class ReaderInterfaceWindow(FramelessWindow):
    def __init__(self, metadata):
        super().__init__()

        if sys.platform == "win32":
            import ctypes

            # Set Taskbar icon
            self.setWindowIcon(QIcon(":/reader/images/book-open.svg"))
            myappid = "epub-reader.reader.v1.0.0"  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        # COMMENT FOR WEB DEBUG
        self.vBoxLayout = QVBoxLayout(self)

        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()

        self.metadata = metadata

        self.button = SettingsOpenButton(FIF.MENU, "", True, self, metadata=metadata)
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
        self.WM_PREVMESSAGE = None

        # DEBUGGING WEB
        # UNCOMMENT FOR WEB DEBBUGING
        # self.dev_view = QWebEngineView()
        # self.book_view.page().setDevToolsPage(self.dev_view.page())
        # self.dev_view.show()

    def __initWidget(self):
        self.resize(640, 740)
        self.vBoxLayout.setContentsMargins(0, self.titleBar.height(), 0, 0)
        self.vBoxLayout.addWidget(self.book_view)

        # STYLE
        StyleSheet.BOOK_WINDOW_INTERFACE.apply(self)
        self.book_view.setFocus()

    def fontSizeChanged(self, size):
        self.book_view.web_communicator.setFontSize_(size)

    def marginSizeChanged(self, size):
        # self.book_view.web_communicator.
        self.book_view.web_communicator.setMarginSize_(size)

    def bookThemeChanged(self, theme):
        self.book_view.web_communicator.setBookTheme_(theme)

    def closeEvent(self, a0: QCloseEvent) -> None:
        # SAVE TO DATA BASE WHEN WINDOW IS CLOSING

        book_storage = self.book_view.web_communicator.book_storage

        self.metadata["currentCFI"] = book_storage["currentCFI"]
        self.metadata["sliderValue"] = book_storage["sliderValue"]
        self.metadata["settings"] = book_storage["settings"]
        self.metadata["progress"] = book_storage["progress"]

        SaveBook = Query()
        Books.update(book_storage, SaveBook.hash == self.metadata["hash"])
        return super().closeEvent(a0)

    def nativeEvent(self, eventType, message):
        """
        CHECK WHEN WINDOW IS DONE RESIZING
        """
        msg = ctypes.wintypes.MSG.from_address(message.__int__())

        if eventType == "windows_generic_MSG":
            if msg.message == win32con.WM_MOVE:
                self.WM_PREVMESSAGE == "MOVE"

            if msg.message == win32con.WM_SIZING:
                self.WM_PREVMESSAGE = "RESIZED"

            if msg.message == win32con.WM_EXITSIZEMOVE:
                if self.WM_PREVMESSAGE == "RESIZED":
                    # RELOAD WEB PAGE WHEN RESIZE IS DONE
                    # THIS FIXES BROKEN EVENTS
                    # TODO : FIND A BETTER WAY TO HANLE THIS
                    self.book_view.web_communicator.handleReloadWindowSig.emit()
                self.WM_PREVMESSAGE = None

        return super().nativeEvent(eventType, message)
