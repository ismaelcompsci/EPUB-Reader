import base64
import copy


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
from utils.utils import (
    BookHandler,
    find_html_dir,
)


# APPEND SCRIPT ON EVERY PAGE IN THE BOOK
# CREATE BRIDGE / WEBCHANNEL


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
        metadata: dict,
    ):
        super().__init__(parent)
        self.style_ = None
        self.has_scrollbar = True

        self.filepath = path
        self.temppath = temp
        self.db = database
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

        handle = BookHandler(self.filepath, self.temppath, self.db)
        book_found, _, content = handle.read_saved_book()

        self.this_book = book_found
        self.this_book["content"] = content
        self.this_book["cover"] = base64.b64decode(book_found["cover"])

        # INITIALIZE BOOK WITH PREVIOUS SETTTINGS
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

        self.scroll_webpage_behavior()

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

        # self.queue_func(lambda: self.page().runJavaScript(script))
        self.queue_func(lambda: self.page().runJavaScript("window.scrollTo(0, 50);"))

        self.setFocus()

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

    def scroll_webpage_behavior(self):
        """
        Adds scroll to next page behavior
        """
        height = self.height()

        script = (
            f"var is_scroll = false;"
            f"var count = 0;"
            f"var up_count = 0;"
            f"var prev_scroll = 0;"
            f"console.log(document.body.scrollHeight , {height});"
            f"if (document.body.scrollHeight > {height}) {{"
            f"    is_scroll = true;"
            f'    console.log("PAGE HAS SCROLL BAR");'
            f"}}"
            f"if (!is_scroll) {{"
            f'    console.log("no-scroll-bar");'
            f"}} else {{"
            f'    console.log("has-scroll-bar");'
            f"}}"
            f'let topelement = document.createElement("div");'
            f'topelement.style.cssText = "height:25px;";'
            f"document.body.prepend(topelement);"
            f'document.addEventListener("scroll", function scrolling(e) {{'
            f"    let documentHeight = document.body.scrollHeight;"
            f"    let currentScroll = window.scrollY + window.innerHeight;"
            f"    let modifier = 1;"
            f"    if (currentScroll + modifier > documentHeight) {{"
            f'        let element = document.createElement("div");'
            f'        element.style.cssText = "height:50px;";'
            f"        document.body.append(element);"
            f"        count += 1;"
            f"    }}"
            f"    if (!window.pageYOffset) {{"
            f'        let topelemnt_ = document.createElement("div");'
            f'        topelemnt_.style.cssText = "height:25px;";'
            f"        document.body.prepend(topelemnt_);"
            f"        window.scrollTo(0, 25);"
            f"        up_count += 1;"
            f"    }}"
            f"    if (up_count > 3) {{"
            f"        console.log(-1);"
            f'        document.removeEventListener("scroll", scrolling);'
            f"        return;"
            f"    }}"
            f"    if (count > 3) {{"
            f'        document.removeEventListener("scroll", scrolling);'
            f"        console.log(1);"
            f"        return;"
            f"    }}"
            f"}});"
        )

        self.insert_script(script, "scroll_behavior")

    def set_font_size(self, size: int) -> None:
        """
        Changes Font size
        """
        self.set_settings("font_size", size)
        self.settings().setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, size)

    def set_background_color(self, color: str | QColor) -> None:
        """
        Queues change background-color change to run when page is done loading
        """
        self.set_settings("background_color", color)
        self.page().setBackgroundColor(color)

    def web_view_css(self, css: str) -> None:
        """
        Adds css code on whole browser
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

        Save = Query()
        self.db.upsert(new_metadata, Save.hash == self.file_md5)

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

    # def event(self, e):
    #     if e.type() in (QEvent.Show, QEvent.Resize):
    #         widget_w = self.frameGeometry().width()
    #         widget_h = self.frameGeometry().height()
    #         screen_w = self.width()
    #         screen_h = self.height()

    #         # For "debugging" purposes:
    #         print(widget_w, widget_h)
    #         print(screen_w, screen_h)

    #         return ((widget_w, widget_h), (screen_w, screen_h))

    # return {"widget": {"width": widget_w, "height": widget_h}, "screen": {"width": screen_w, "height": screen_h}}
