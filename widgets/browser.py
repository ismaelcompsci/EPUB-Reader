import base64
import os
import typing
from PyQt5 import QtWebEngineCore


from PyQt5.QtCore import QUrl, QObject, pyqtSlot
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtWidgets import QWidget
from config.config import cfg, PROJECT_DIR


def get_index_html():
    return os.path.join(PROJECT_DIR, "resource", "html") + "\index.html"


class Page(QWebEnginePage):
    """
    Page for WebEnginView
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        # Secure Web
        s = self.settings()
        a = s.setAttribute

        a(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        a(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        a(QWebEngineSettings.WebAttribute.JavascriptCanAccessClipboard, True)
        a(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        a(QWebEngineSettings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        a(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        a(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        print("javaScriptConsoleMessage: ", level, msg, linenumber, source_id)


class BookWebCommunication(QObject):
    def __init__(self) -> None:
        super().__init__()

        self.file_name = None

    @pyqtSlot(result=str)
    def getFile(self):
        file = self.file_name

        file = file.replace(" ", "%20")
        return file

    


class BookWebView(QWebEngineView):
    """
    Displays html from book
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._page = Page(self)
        self.setPage(self._page)



