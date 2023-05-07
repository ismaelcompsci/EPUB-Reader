import json
import os

from epub_reader.config.config import PROJECT_DIR
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineSettings, QWebEngineView
from PyQt5.QtWidgets import QWidget


def get_index_html():
    print(os.path.join(PROJECT_DIR, "app", "html") + os.path.sep + "index.html")
    return os.path.join(PROJECT_DIR, "app", "html") + os.path.sep + "index.html"


class Page(QWebEnginePage):
    """
    Page for WebEnginView
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Secure Web
        s = self.settings()
        a = s.setAttribute

        # a(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        # a(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        # a(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        # a(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        # a(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        # a(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        # a(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        print("javaScriptConsoleMessage: ", level, msg, linenumber)


# SORTED BY NAME
# SORTED BY DATE ADDED
# SORTED BY AUTHOR
# SORTED BY


class BookWebCommunication(QObject):
    fontSizeChanged = pyqtSignal(int)
    marginSizeChanged = pyqtSignal(int)
    chapterChanged = pyqtSignal(str)
    bookThemeChanged_ = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.file_name = None
        self.book_storage = {}

    @pyqtSlot(result=str)
    def getBookStorage(self):
        return json.dumps(self.book_storage)

    @pyqtSlot(str)
    def setBookStorage(self, new_book_data):
        self.book_storage = json.loads(new_book_data)

    @pyqtSlot(result=str)
    def getFile(self):
        # SOME FILE PATHS HAVE SPACES AND EPUBJS CANT OPEN THEM
        # FIGURE A WAY TO FIX IT BEFORE SENDING TO JAVASCRIPT
        # OR A WAY IN JAVASCRIPT

        # FILE PATHS THAT DONT WORK
        # length ?
        # C:\Users\Ismael\AppData\Local\EPUB-Reader\EPUB-Reader\Books\Barren_The_Complete_Trilogy_Box_Set_by__(Zach_Bohannon)__(J._Thorn)_(#1-3).epub
        #
        file = self.file_name
        # file = file.replace(" ", "%20")
        return file

    @pyqtSlot(result=int)
    def getMarginSize(self):
        return self.book_storage["settings"]["margin"]

    @pyqtSlot(result=int)
    def setMarginSize_(self, size):
        self.book_storage["settings"]["margin"] = size
        self.marginSizeChanged.emit(size)

    @pyqtSlot(result=int)
    def getFontSize_(self):
        return self.book_storage["settings"]["fontSize"]

    @pyqtSlot(int, result=int)
    def setFontSize_(self, size):
        self.book_storage["settings"]["fontSize"] = size
        self.fontSizeChanged.emit(size)

    @pyqtSlot(result=int)
    def getBookTheme(self):
        return self.book_storage["settings"]["theme"]

    @pyqtSlot(int, result=int)
    def setBookTheme_(self, theme):
        self.book_storage["settings"]["theme"] = theme
        self.bookThemeChanged_.emit(theme)


class BookWebView(QWebEngineView):
    """
    Displays html from book
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._page = Page(self)
        self.setPage(self._page)
