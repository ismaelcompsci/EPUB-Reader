

from tinydb import Query, TinyDB

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebChannel import QWebChannel


from PyQt5.QtWidgets import *
from qframelesswindow import *

from .browser import BookWebView, BookWebCommunication, get_index_html


# CURRENTLY WORK SITH TWO HTML TAGS??? 
# SET FILEPATH WITH QWEBCHANNEL 
# IF THAT DOES NOT WORK
# USE BS4 TO INPUT THE FILE
# OR MAKE A SCRIPT AND AADDD TO SCRIPT TAG


class BookViewer(BookWebView):
    """
    displays epub html
    """

    def __init__(
        self,
        parent: QWidget,
        book_path: str,
        temp_dir: str,
        file_md5: str,
        database: TinyDB,
        metadata: dict,
    ):
        super().__init__(parent)

        self.book_path = book_path
        self.temp_dir = temp_dir
        self.file_md5 = file_md5
        self.metadata = metadata
        self.database = database

        self.web_communicator = BookWebCommunication()
        self.web_communicator.file_name = self.book_path

        self.web_communicator.book_storage = {
            "hash": self.file_md5,
            "currentCFI": self.metadata["currentCFI"],
            "sliderValue": self.metadata["sliderValue"],
            "settings": self.metadata["settings"],
            "progress": self.metadata["progress"],
        }

        self.web_channel = QWebChannel(self.page())
        self.web_channel.registerObject("backend", self.web_communicator)
        self.page().setWebChannel(self.web_channel)


        self.load(QUrl.fromLocalFile(get_index_html()))

        
        self.__initWeb()
        self.setContentsMargins(0, 0, 0, 0)

    def __initWeb(self):
        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ShowScrollBars, False
        )