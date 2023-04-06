import base64
import copy
import json
import os


from epub_tools.epub import ParseEPUB
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *

from PySide6.QtWidgets import *
from qframelesswindow import *


from components.web_view import WebView
from utils.utils import resize_image, add_css_to_html

# EPUB IS p tag is a block
# count blocks
# check which block we are in
# set that block to the top

# DISPLAYS HTML FROM BOOK
class EReader(WebView):
    """
    Web View for Html
    """

    def __init__(self, parent, path, temp, file_md5):
        super().__init__(parent)

        self.filepath = path
        self.temppath = temp

        self.file_md5 = file_md5
        self.settings_ = {}

        self.setMouseTracking(True)
        self.page().scrollPositionChanged.connect(self.scroll_position_changed)

        # self.verticalScrollBar().sliderMoved.connect(self.record_position)

    def load_book(self):
        """
        Initialize epub file
        """

        # TODO
        # CHECK IF BOOK ALREADY EXISTS
        # GET DATA FROM DATABASE

        # TODO
        # IF NEW BOOK
        # ADD TO DATABASE

        # NEW BOOK
        book = ParseEPUB(self.filepath, self.temppath, self.file_md5)

        book.read_book()  # INITIALIZE BOOK
        metadata = book.generate_metadata()  # FOR ADDING TO DB
        toc, content, images_only = book.generate_content()  # FOR READING

        self.this_book = {}

        self.this_book[self.file_md5] = {
            "hash": self.file_md5,
            "path": self.filepath,
        }

        cover_image = resize_image(metadata.cover)

        self.this_book[self.file_md5]["position"] = {}
        self.this_book[self.file_md5]["bookmarks"] = None
        self.this_book[self.file_md5]["toc"] = toc
        self.this_book[self.file_md5]["content"] = content
        self.this_book[self.file_md5]["cover"] = cover_image
        self.this_book[self.file_md5]["title"] = metadata.title
        self.this_book[self.file_md5]["author"] = metadata[1]
        self.this_book[self.file_md5]["year"] = metadata[2]
        self.this_book[self.file_md5]["isbn"] = metadata[3]
        self.this_book[self.file_md5]["tags"] = metadata[4]

    def set_content(self, position):
        """
        Sets html in webengine
        """

        try:

            content = self.this_book[self.file_md5]["content"][position]
            # print(content)

        except IndexError:
            return

        self.this_book[self.file_md5]["position"]["current_chapter"] = position
        self.this_book[self.file_md5]["position"]["is_read"] = False

        self.setHtml(
            content,
            baseUrl=QUrl.fromLocalFile(
                os.path.join(self.temppath, self.file_md5, "OEBPS", "images")
            ),
        )
        self.save_book_data()

        self.setFocus()

    def change_chapter(self, direction):
        """
        Changes chapter forward or backwords
        """
        current_position = self.this_book[self.file_md5]["position"]["current_chapter"]
        final_position = len(self.this_book[self.file_md5]["content"])

        # PREVENT SCROLLING BELOW PAGE 1
        if current_position == 0 and direction == -1:
            return

        # PREVENT SCROLLING BEYOND LAST PAGE
        if current_position == final_position and direction == 1:
            return

        self.set_content(current_position + direction)

    def set_font_size(self, size):
        """
        Changes Font size
        """
        self.settings().setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, size)

    def bg_buttons_toggled(self, button):
        """
        Checks which radiobutton is toggled
        """
        if button.text() == "Dark" and button.isChecked():
            self.web_view_css("html {color: white;}")
            self.set_background_color("#18181b")

        if button.text() == "Light" and button.isChecked():
            self.set_background_color("white")

    def set_background_color(self, color):
        """
        Queues change background-color change to run when page is done loading
        """
        self.settings_["color"] = color
        self.page().setBackgroundColor(self.settings_["color"])

    def web_view_css(self, css):
        """
        Runs javascript code on
        """

        script = f'(function() {{ css = document.createElement("style"); css.type = "text/css"; document.head.appendChild(css); css.innerText = "{css}";}})()'
        script_ = QWebEngineScript()

        self.page().runJavaScript(
            script, QWebEngineScript.ScriptWorldId.ApplicationWorld
        )
        script_.setName("style")
        script_.setSourceCode(script)
        script_.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script_.setRunsOnSubFrames(True)
        script_.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
        self.page().scripts().insert(script_)

    def scroll_position_changed(self, height):
        # print(height)
        pass

    def keyPressEvent(self, ev) -> None:
        """
        Keyboard arrows to change page
        """
        key = ev.key()

        if key == Qt.Key.Key_Right:
            self.change_chapter(1)
        if key == Qt.Key.Key_Left:
            self.change_chapter(-1)

        return super().keyPressEvent(ev)

    def save_book_data(self):
        new_metadata = copy.deepcopy(self.this_book)
        new_metadata[self.file_md5].pop("content")

        # ENCODED IMAGE
        image = base64.b64encode(new_metadata[self.file_md5]["cover"]).decode("utf-8")
        # DECODE -> base64.b64decode(encoded_image)

        new_metadata[self.file_md5]["cover"] = image

        database_path = os.path.join(self.temppath, "db")

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        with open(os.path.join(database_path, f"{self.file_md5}.json"), "w") as f:
            json.dump(new_metadata, f)

    # def test(self):
    #     script = "console.log(window.pageXOffset, window.pageYOffset)"
    #     self.page().runJavaScript(
    #         script, QWebEngineScript.ScriptWorldId.ApplicationWorld
    #     )
