from epub_reader.app.utils.style_sheet import StyleSheet
from epub_reader.app.widgets.book_view import BookViewer
from epub_reader.app.widgets.settingsinterface import SettingsOpenButton
from epub_reader.config.config import EXTRACTED_EPUB_DIR, Books
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QVBoxLayout
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, StandardTitleBar
from tinydb import Query


class ReaderInterfaceWindow(FramelessWindow):
    def __init__(self, metadata):
        super().__init__()
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
