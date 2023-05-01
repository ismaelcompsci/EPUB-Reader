import base64
import json
import os
import typing

from config.config import PROJECT_DIR, cfg
from PyQt5 import QtWebEngineCore
from PyQt5.QtCore import QEvent, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import (QWebEnginePage, QWebEngineSettings,
                                      QWebEngineView)
from PyQt5.QtWidgets import QWidget
from qfluentwidgets.common import isDarkTheme, themeColor


def get_index_html():
    return os.path.join(PROJECT_DIR, "resource", "html") +os.path.sep +"index.html"


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
        print("javaScriptConsoleMessage: ", level, msg, linenumber)


class BookWebCommunication(QObject):
    themeChanged = pyqtSignal(str)
    chapterChanged = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.file_name = None
        self.book_storage = {}


        
    @pyqtSlot(result=str)
    def getBookStorage(self):
        return  json.dumps(self.book_storage)
    

    @pyqtSlot(str)
    def setBookStorage(self, new_book_data):
        self.book_storage =json.loads(new_book_data)


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
    
    # @pyqtSlot(result=str)
    # def getTheme(self):
    #     return self.theme_

    # @pyqtSlot(str, result=str)
    # def setTheme(self, theme):
    #     self.theme = theme
    #     self.themeChanged.emit(theme)


    # def chapterChangedEvent(self, direction):
    #     self.chapterChanged.emit(direction)



class BookWebView(QWebEngineView):
    """
    Displays html from book
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._page = Page(self)
        self.setPage(self._page)



