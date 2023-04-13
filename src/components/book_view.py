import base64
import copy
import datetime
import json
import os
import pathlib

import PySide6
from tinydb import Query, TinyDB


from epub_tools.epub import ParseEPUB
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWebEngineWidgets import *
from PySide6.QtWebEngineCore import *

from PySide6.QtWidgets import *
from qframelesswindow import *


from components.web_view import WebView
from utils.utils import resize_image, add_css_to_html, file_md5_


# APPEND SCRIPT ON EVERY PAGE IN THE BOOK
# CREATE BRIDGE / WEBCHANNEL


def find_html_dir(temp: str, file_md5: str) -> str:
    """
    Find html dir for setHtml baseUrl
    """
    base_dir = os.path.join(temp, file_md5)

    for path, subdirs, files in os.walk(base_dir):
        html_file_count = sum(1 for name in files if "htm" in name)
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
        self, file: str, temp_dir: str, database: TinyDB, query: Query
    ) -> None:
        self.db = database
        self.query = query

        self.file = file
        self.temp_dir = temp_dir

    def hash_book(self) -> str:
        md5_ = file_md5_(self.file)
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

        cover_image = resize_image(metadata.cover)

        self.this_book = {
            "hash": self.md5_,
            "path": self.file,
            "position": {},
            "bookmarks": None,
            "toc": toc,
            "content": content,
            "cover": cover_image,
            "title": metadata.title,
            "author": metadata[1],
            "year": metadata[2],
            "isbn": metadata[3],
            "tags": metadata[4],
            "date_added": datetime.datetime.now().timestamp() * 1000,
        }

    def read_saved_book(self) -> tuple:
        """
        Reads book in database
        """
        self.file_md5 = self.hash_book()

        book_found = self.db.get(self.query.hash == self.file_md5)

        book = ParseEPUB(self.file, self.temp_dir, self.file_md5)
        book.read_book()
        toc, content, images_only = book.generate_content()

        return (book_found, toc, content)

    def save_book(self) -> None:
        """
        Initialize epub file
        """
        # CHECK IF BOOK ALREADY EXISTS
        book = self.db.get(self.query.hash == self.md5_)
        if book:
            return

        # IF NEW BOOK
        # ADD TO DATABASE
        self.save_new_book()

    def save_new_book(self) -> None:
        """
        Saves new book
        """
        new_metadata = copy.deepcopy(self.this_book)
        new_metadata.pop("content")

        # ENCODED IMAGE
        image = base64.b64encode(new_metadata["cover"]).decode("utf-8")
        # DECODE -> base64.b64decode(encoded_image)

        new_metadata["cover"] = image

        self.db.insert(new_metadata)


class EReader(WebView):
    """
    Web View for Html
    """

    def __init__(
        self,
        parent: QWidget,
        path: str,
        temp: str,
        file_md5: str,
        database: TinyDB,
        query: Query,
        metadata: dict,
    ):
        super().__init__(parent)
        self.style_ = None
        self.has_scrollbar = True

        self.filepath = path
        self.temppath = temp
        self.db = database
        self.query = query
        self.metadata = metadata

        self.file_md5 = file_md5
        self.settings_ = {}

        self.base_url = find_html_dir(self.temppath, self.file_md5)

        self.setMouseTracking(True)

        self.scroll_height = 0
        self.page().scrollPositionChanged.connect(self.scroll_position_changed)

    def load_book(self) -> None:
        """
        Initialize epub file
        """

        # TODO
        # CALL BOOKHANDLER INSTEAD
        # BookHandler(self.filepath, self.temppath, self.filemd5, self.db) -> book

        # GET DATA FROM DATABASE

        handle = BookHandler(self.filepath, self.temppath, self.db, self.query)
        book_found, _, content = handle.read_saved_book()

        self.this_book = book_found
        self.this_book["content"] = content
        self.this_book["cover"] = base64.b64decode(book_found["cover"])
        # SET SCROLL POS
        self.scroll_y = None
        if "scroll_position" in self.this_book:
            # self.parent().
            self.scroll_y = self.this_book["scroll_position"]

        # CHECK IF WE HAVE A RECORDED POS
        if len(self.this_book["position"]) == 0:
            self.set_content(0)

        else:
            # SET CHAPTER POS
            self.set_content(int(self.this_book["position"]["current_chapter"]))
            self.scroll_to(self.scroll_y)

        # SET RECORDED WINDOW SIZE
        if "window_size" in self.this_book:
            w = int(self.this_book["window_size"]["width"])
            h = int(self.this_book["window_size"]["height"])

            self.parent().resize(w, h)
        else:
            self.parent().resize(600, 900)

        if "style" in self.this_book:
            style = self.this_book["style"]
            self.presets(style)

        else:
            self.set_content(0)

    def set_content(self, position: int) -> None:
        """
        Sets html in webengine
        """
        try:
            content = self.this_book["content"][position]

        except IndexError:
            return

        self.this_book["position"]["current_chapter"] = position
        self.this_book["position"]["is_read"] = False

        self.setHtml(
            content,
            baseUrl=QUrl.fromLocalFile(self.base_url),
        )

        script = """
            var is_scroll =false
            if (document.body.scrollWidth > document.body.clientWidth || document.body.scrollHeight > document.body.clientHeight){
                is_scroll = true
            }

            if (!is_scroll){
            console.log("no-scroll-bar")
            } else {
            console.log("has-scroll-bar")
            }

            let topelemnt = document.createElement('div');
            topelemnt.style.cssText = 'height:50px;';
            document.body.prepend(topelemnt)

            console.log(document.body.scrollHeight,window.scrollY)

            var count = 0
            var up_count = 0
            var prev_scroll = 0
            document.addEventListener('scroll', function s(e) {
                let documentHeight = document.body.scrollHeight;
                let currentScroll = window.scrollY + window.innerHeight;

                let modifier = 1;
                if(currentScroll + modifier > documentHeight) {
                let element = document.createElement('div');
                element.style.cssText = 'height:50px;';
                document.body.append(element);
                count+=1
                }

                if (!window.pageYOffset){
                    let topelemnt = document.createElement('div');
                    topelemnt.style.cssText = 'height:25px;';
                    document.body.prepend(topelemnt)
                    window.scrollTo(0, 25)
                    up_count += 1

                }
                
                if(up_count > 3){
                console.log(-1)
                document.removeEventListener("scroll", s)
                return
                }

                if (count > 3){
                
                document.removeEventListener("scroll", s)
                console.log(1)
                return
                }
        })
            """

        self.queue_func(lambda: self.page().runJavaScript(script))
        self.setFocus()
        self.queue_func(lambda: self.page().runJavaScript("window.scrollTo(0, 50);"))

    def handle_(self, response):
        if response:
            if response == "1":
                self.change_chapter(1)

            if response == "-1":
                self.change_chapter(-1, True)

            if response == "no-scroll-bar":
                self.has_scrollbar = False

            if response == "has-scroll-bar":
                self.has_scrollbar = True

    def change_chapter(self, direction: int, scroll_botom: bool = False) -> None:
        """
        Changes chapter forward or backwords
        """
        current_position = self.this_book["position"]["current_chapter"]
        final_position = len(self.this_book["content"])

        # PREVENT SCROLLING BELOW PAGE 1
        if current_position == 0 and direction == -1:
            return

        # PREVENT SCROLLING BEYOND LAST PAGE
        if current_position == final_position and direction == 1:
            return

        self.set_content(current_position + direction)

        if scroll_botom:
            self.queue_func(
                lambda: self.page().runJavaScript(
                    """window.scrollTo(0, document.body.scrollHeight);"""
                )
            )

        self.setFocus()

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
            self.web_view_css("html {color: white;, background-color: black;}")
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
        self.insert_script(script, "style")

    def insert_script(self, script, name):
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

        return script_

    def scroll_position_changed(self, height):
        self.scroll_height = height

    def scroll_to(self, pos):
        # SET SCROLL POS
        self.queue_func(lambda: self.page().runJavaScript(f"window.scrollTo(0, {pos})"))

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
        new_metadata.pop("content")

        # ENCODED IMAGE
        image = base64.b64encode(new_metadata["cover"]).decode("utf-8")
        # DECODE -> base64.b64decode(encoded_image)

        new_metadata["cover"] = image

        self.db.update(new_metadata, self.query.hash == self.file_md5)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if not self.has_scrollbar:
            delta = event.angleDelta().y()
            if delta > 0:
                # scrolling up
                self.change_chapter(-1)
            elif delta < 0:
                # scrolling down
                self.change_chapter(1)
        return super().wheelEvent(event)
