import base64
import copy
import datetime
import json
import os
import pathlib

import PySide6


from epub_tools.epub import ParseEPUB
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *

from PySide6.QtWidgets import *
from qframelesswindow import *


from components.web_view import WebView
from utils.utils import resize_image, add_css_to_html, file_md5_


def find_html_dir(temp: str, file_md5: str) -> str:
    """
    Find html dir for setHtml baseUrl
    """
    base_dir = os.path.join(temp, file_md5)

    for path, subdirs, files in os.walk(base_dir):
        html_file_count = 0
        for name in files:
            if "htm" in name:
                html_file_count += 1
                if html_file_count >= 2:
                    # return a dir with 2 or more html files
                    return str(pathlib.Path(path).resolve()) + os.path.sep
    # Return the temp dir of the book
    return os.path.join(temp, file_md5) + os.path.join


# DISPLAYS HTML FROM BOOK
class BookHandler:
    """
    Adds book to db
    """

    def __init__(
        self, file: str, db_path: str = None, settings: str = None, temp_dir: str = None
    ) -> None:
        self.file = file
        self.database_path = db_path
        self.settings = settings
        self.temp_dir = temp_dir

    def hash_book(self) -> str:
        md5_ = file_md5_(self.file)
        # print("hash: ", md5_)
        return md5_

    def read_book(self):

        self.md5_ = self.hash_book()

        # BOOK DATA
        self.parsed_book = ParseEPUB(self.file, self.temp_dir, self.md5_)
        # NEW BOOK
        self.parsed_book.read_book()  # INITIALIZE BOOK
        metadata = self.parsed_book.generate_metadata()  # FOR ADDING TO DB
        toc, content, images_only = self.parsed_book.generate_content()  # FOR READING

        self.this_book = {}

        self.this_book[self.md5_] = {
            "hash": self.md5_,
            "path": self.file,
        }

        cover_image = resize_image(metadata.cover)

        self.this_book[self.md5_]["position"] = {}
        self.this_book[self.md5_]["bookmarks"] = None
        self.this_book[self.md5_]["toc"] = toc
        self.this_book[self.md5_]["content"] = content
        self.this_book[self.md5_]["cover"] = cover_image
        self.this_book[self.md5_]["title"] = metadata.title
        self.this_book[self.md5_]["author"] = metadata[1]
        self.this_book[self.md5_]["year"] = metadata[2]
        self.this_book[self.md5_]["isbn"] = metadata[3]
        self.this_book[self.md5_]["tags"] = metadata[4]
        self.this_book[self.md5_]["date_added"] = (
            datetime.datetime.now().timestamp() * 1000
        )

    def save_book(self) -> None:
        """
        Initialize epub file
        """
        # CHECK IF BOOK ALREADY EXISTS
        if f"{self.md5_}.json" in os.listdir(os.path.join(self.temp_dir, "db")):
            return

        # IF NEW BOOK
        # ADD TO DATABASE
        self.save_new_book()

    def save_new_book(self) -> None:
        """
        Saves new book
        """
        new_metadata = copy.deepcopy(self.this_book)
        new_metadata[self.md5_].pop("content")

        # ENCODED IMAGE
        image = base64.b64encode(new_metadata[self.md5_]["cover"]).decode("utf-8")
        # DECODE -> base64.b64decode(encoded_image)

        new_metadata[self.md5_]["cover"] = image

        database_path = os.path.join(self.temp_dir, "db")

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        with open(os.path.join(database_path, f"{self.md5_}.json"), "w") as f:
            json.dump(new_metadata, f)

        # print("DONE SAVEING")


class EReader(WebView):
    """
    Web View for Html
    """

    next_chapter = Signal(str)

    def __init__(self, parent: QWidget, path: str, temp: str, file_md5: str):
        super().__init__(parent)
        self.style_ = None

        self.filepath = path
        self.temppath = temp

        self.file_md5 = file_md5
        self.settings_ = {}

        self.base_url = find_html_dir(self.temppath, self.file_md5)

        self.setMouseTracking(True)

        self.scroll_height = 0
        self.page().scrollPositionChanged.connect(self.scroll_position_changed)

        self.run_func(lambda: self.hide())

        # self.next_chapter.connect(self.changing)

    def load_book(self) -> None:
        """
        Initialize epub file
        """

        # GET DATA FROM DATABASE
        book_data_path = os.path.join(self.temppath, "db", f"{self.file_md5}.json")

        if os.path.exists(book_data_path):
            with open(book_data_path, "r") as f:
                book_found = json.loads(f.read())

                book = ParseEPUB(self.filepath, self.temppath, self.file_md5)

                book.read_book()
                toc, content, images_only = book.generate_content()

                self.this_book = book_found
                self.this_book[self.file_md5]["content"] = content
                self.this_book[self.file_md5]["cover"] = base64.b64decode(
                    book_found[self.file_md5]["cover"]
                )
            # SET SCROLL POS
            self.scroll_y = None
            if "scroll_position" in self.this_book[self.file_md5]:
                # self.parent().
                self.scroll_y = self.this_book[self.file_md5]["scroll_position"]

            # CHECK IF WE HAVE A RECORDED POS
            if len(self.this_book[self.file_md5]["position"]) == 0:
                self.set_content(0)

            else:
                # SET CHAPTER POS
                self.set_content(
                    int(self.this_book[self.file_md5]["position"]["current_chapter"])
                )
                self.scroll_to(self.scroll_y)

            # SET RECORDED WINDOW SIZE
            if "window_size" in self.this_book[self.file_md5]:
                w = int(self.this_book[self.file_md5]["window_size"]["width"])
                h = int(self.this_book[self.file_md5]["window_size"]["height"])

                self.parent().resize(w, h)
            else:
                self.parent().resize(600, 900)

            if "style" in self.this_book[self.file_md5]:
                style = self.this_book[self.file_md5]["style"]
                self.presets(style)

            else:
                self.set_content(0)

    def set_content(self, position: int) -> None:
        """
        Sets html in webengine
        """
        self.queue_func(lambda: self.show())

        try:

            content = self.this_book[self.file_md5]["content"][position]

        except IndexError:
            return

        self.this_book[self.file_md5]["position"]["current_chapter"] = position
        self.this_book[self.file_md5]["position"]["is_read"] = False

        # TODO
        # ----------------****------------
        # FIND DIRECTORY WITH HTML FILES
        # 26eba5498bb8250d008595b74c7b33d0 -> OEBPS -> 1.HTML, 2.HTML
        # FULL DIR IS temppath\26eba5498bb8250d008595b74c7b33d0\OEBPS\    <- ANSWER

        self.setHtml(
            content,
            baseUrl=QUrl.fromLocalFile(self.base_url),
        )
        self.save_book_data()

        # self.page_height = self.queue_func(
        #     lambda: self.page().runJavaScript(
        #         "console.log(document.documentElement.scrollHeight)", self.get_height
        #     )
        # )

        #     script = """
        #     var count = 0
        #         document.addEventListener('scroll', function s(e) {
        #     let documentHeight = document.body.scrollHeight;
        #     let currentScroll = window.scrollY + window.innerHeight;
        #     // When the user is [modifier]px from the bottom, fire the event.
        #     let modifier = 1;
        #     if(currentScroll + modifier > documentHeight) {
        #     let element = document.createElement('div');
        #     element.style.cssText = 'height:50px;';
        #     document.body.append(element);
        #     count+=1
        #     }

        #     if (count > 3){
        #     console.log(1)
        #     document.removeEventListener("scroll", s)
        #     return
        #     }

        # })

        #     """

        # self.queue_func(lambda: self.page().runJavaScript(script, 0, self.__callback))
        self.setFocus()

    # def __callback(self, response):

    #     # if response:
    #     print("js response: ", response, end="")
    #     if response:
    #         print("hfaswdf;lasdfkj")

    #     self.next_chapter.emit(response)

    def change_chapter(self, direction: int) -> None:
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

    def set_font_size(self, size: int) -> None:
        """
        Changes Font size
        """
        self.set_settings("font_size", size)
        self.settings().setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, size)

    def bg_buttons_toggled(self, button: QRadioButton) -> None:
        """
        Checks which radiobutton is toggled
        """
        if button.text() == "Dark" and button.isChecked():
            self.presets("Dark")

        if button.text() == "Light" and button.isChecked():
            self.presets("Light")

    def presets(self, style):
        self.style_ = style

        if style == "Dark":
            self.web_view_css("html {color: white;}")
            self.set_background_color("#18181b")

        if style == "Light":
            self.set_background_color("white")
            self.web_view_css("html {color: black;}")

    def set_background_color(self, color: str) -> None:
        """
        Queues change background-color change to run when page is done loading
        """
        self.set_settings("background_color", color)
        self.page().setBackgroundColor(color)

    def web_view_css(self, css: str) -> None:
        """
        Runs javascript code on
        """

        script = f'(function() {{ css = document.createElement("style"); css.type = "text/css"; document.head.appendChild(css); css.innerText = "{css}";}})()'
        self.inser_script(script, "style")

    def inser_script(self, script, name):
        script_ = QWebEngineScript()

        self.page().runJavaScript(
            script, QWebEngineScript.ScriptWorldId.ApplicationWorld
        )
        script_.setName(name)
        script_.setSourceCode(script)
        script_.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script_.setRunsOnSubFrames(True)
        script_.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)

        self.page().scripts().insert(script_)

    def scroll_position_changed(self, height):
        self.scroll_height = height

    def scroll_to(self, pos):
        # SET SCROLL POS
        self.queue_func(lambda: self.page().runJavaScript(f"window.scrollTo(0, {pos})"))

    # def wheelEvent(self, event: QWheelEvent) -> None:
    #     print(self.height_)
    #     if not self.loading:
    #         bias = event.angleDelta().y()
    #         print(bias)

    def keyPressEvent(self, ev: QKeyEvent) -> None:
        """
        Keyboard arrows to change page
        """

        key = ev.key()

        if key == Qt.Key.Key_Right:
            self.change_chapter(1)
        if key == Qt.Key.Key_Left:
            self.change_chapter(-1)

        return super().keyPressEvent(ev)

    def set_settings(self, key: str, value: str | int):
        self.settings_[key] = value

    def save_book_data(self) -> None:
        """
        Saves book data to db
        """
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
