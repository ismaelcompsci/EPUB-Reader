import base64
import copy
import os
from bs4 import BeautifulSoup

from tinydb import Query, TinyDB

from utils.utils import find_html_dir
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebChannel import QWebChannel


from PyQt5.QtWidgets import *
from qframelesswindow import *

from .browser import BookWebView, Document
from utils.bookhandler import BookHandler


# TODO
# Resize IMAGE to view height and set width

# TRY ADDING SCRIPT TAG TO HTML LIKE THIS <script src="c:/acutal file location"</script>


# TRY ONLY HAVING ONE WEBPAGE WE INSERT HTML INTO and using javascript we change pages not sethtml


# SIMULATE PAGES WITH JAVASCRIPT INSTEAD OF SETTING HTML

dir = os.getcwd()

js_path = os.path.join(dir, "resource", "js") + os.path.sep


def add_script_src(html):
    soup = BeautifulSoup(html, "html.parser")

    head_tag = soup.find("head")
    script_tag = soup.new_tag(
        "script",
        src=js_path + "qwebchannel_new.js",
    )
    script_tag2 = soup.new_tag(
        "script",
        src=js_path + "reader.js",
    )

    head_tag.append(script_tag)
    head_tag.append(script_tag2)

    return str(soup)


def append_script(html_, api):
    soup = BeautifulSoup(html_, "html.parser")

    script_tag = soup.new_tag("script")
    script_tag.string = api + script

    body_tag = soup.find("body")
    if not body_tag:
        return html_
    body_tag.append(script_tag)

    return str(soup)


script = """


new QWebChannel(qt.webChannelTransport, function (channel) {
  var content = channel.objects.content;

  // set contents font size and margin to page
  setFontSize(content.fontSize_);
  setLeftAndRightMargin(content.margin_);

  // connect event listeners
  content.fontSizeChanged.connect(setFontSize);
  content.marginSizeChanged.connect(setLeftAndRightMargin);
});


function setFontSize(n) {
  document.body.style.fontSize = n + "px";
};

function setLeftAndRightMargin(margin) {
  // Sets l and r margin to "margin"
  document.body.style.marginLeft = 10 * margin + "px";
  document.body.style.marginRight = 10 * margin + "px";
};

function fitImages() {
  // fits images into page
  var images = document.getElementsByTagName("img");
  for (var i = 0; i < images.length; i++) {
    images[i].style.maxWidth = "100%";
    images[i].style.maxHeight = "100vh";
    images[i].style.width = "auto";
    images[i].style.height = "auto";
  }
}
fitImages();

"""


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

        self.base_url = find_html_dir(self.temp_dir, self.file_md5)

        self.__initWeb()

    def __initWeb(self):
        file = QFile(":/reader/js/qwebchannel_new.js")
        if file.open(QIODevice.ReadOnly | QFile.Text):
            self.api_file = QTextStream(file).readAll()
            file.close()

        self.document_js = Document()

        self.web_channel = QWebChannel(self.page())
        self.web_channel.registerObject("content", self.document_js)
        self.page().setWebChannel(self.web_channel)

        self.setMouseTracking(True)
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ShowScrollBars, False
        )
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def load_book(self) -> None:
        """
        Initialize epub file
        """

        handle = BookHandler(self.book_path, self.temp_dir, self.database)
        book_found, _, content = handle.read_saved_book()

        self.this_book = book_found

        self.this_book["content"] = content
        self.this_book["cover"] = base64.b64decode(book_found["cover"])

        if self.this_book.get("position"):
            self.set_content(self.this_book["position"]["current_chapter"])
        else:
            self.set_content(0)

    def set_content(self, position: int) -> None:
        """
        Sets html in webengine

        """
        try:
            content = self.this_book["content"][position]  # update positon in content

        except IndexError:
            return

        self.this_book["position"]["current_chapter"] = position

        self.setHtml(
            add_script_src(content),
            baseUrl=QUrl.fromLocalFile(
                self.base_url
            ),  # SET HTML PATH FOR LOCAL CSS AND IMAGES
        )

        self.scroll_to(0)
        self.setFocus()

        # self.insert_script(
        #     self.api_file, "api", QWebEngineScript.ScriptWorldId.MainWorld
        # )
        # self.insert_script(script, "script", QWebEngineScript.ScriptWorldId.MainWorld)

        self.queue_func(
            lambda: self.document_js.fontSizeChanged.emit(self.document_js.fontSize_)
        )
        self.queue_func(
            lambda: self.document_js.marginSizeChanged.emit(self.document_js.margin_)
        )

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
            # IF -1 scroll to bottom of page
            self.scroll_to("document.body.scrollHeight")

    def insert_web_view_css(self, css: str):
        """
        add css
        """
        script = f'(function() {{ css = document.createElement("style"); css.type = "text/css"; document.head.appendChild(css); css.innerText = "{css}";}})()'
        self.insert_script(script, "style", QWebEngineScript.ScriptWorldId.MainWorld)

    def insert_script(
        self,
        script,
        name,
        applicationid=QWebEngineScript.ScriptWorldId.ApplicationWorld,
    ):
        """
        insert javascript into world
        """
        script_ = QWebEngineScript()

        self.page().runJavaScript(script, applicationid)
        script_.setName(name)
        script_.setSourceCode(script)
        script_.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script_.setRunsOnSubFrames(True)
        script_.setWorldId(applicationid)

        self.page().scripts().insert(script_)

    def scroll_to(self, pos):
        """
        set scroll position
        """
        self.queue_func(lambda: self.page().runJavaScript(f"window.scrollTo(0, {pos})"))

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
        self.database.upsert(new_metadata, Save.hash == self.file_md5)


# NOT USED FOR NOW CLEANING THINGS
# def handle_(self, response):
#     if response:
#         if response == "1":
#             self.change_chapter(1)

#         if response == "-1":
#             self.change_chapter(-1, True)

#         if response == "no-scroll-bar":
#             self.has_scrollbar = False

#         if response == "has-scroll-bar":
#             self.has_scrollbar = True
# def scroll_webpage_behavior(self, w, h):
#     """
#     Adds scroll to next page behavior
#     """
#     if self.inserted_script:
#         return

#     script = (
#         f"var is_scroll = false;"
#         f"var count = 0;"
#         f"var up_count = 0;"
#         f"var prev_scroll = 0;"
#         f"if (document.body.scrollWidth > {w} || document.body.scrollHeight > {h}) {{"
#         f"    is_scroll = true;"
#         f'    console.log("PAGE HAS SCROLL BAR");'
#         f"}}"
#         f"if (!is_scroll) {{"
#         f'    console.log("no-scroll-bar");'
#         f"}} else {{"
#         f'    console.log("has-scroll-bar");'
#         f"}}"
#         f'let topelement = document.createElement("div");'
#         f'topelement.style.cssText = "height:25px;";'
#         f"document.body.prepend(topelement);"
#         f'document.addEventListener("scroll", function scrolling(e) {{'
#         f"    let documentHeight = document.body.scrollHeight;"
#         f"    let currentScroll = window.scrollY + window.innerHeight;"
#         f"    let modifier = 1;"
#         f"    if (currentScroll + modifier > documentHeight) {{"
#         f'        let element = document.createElement("div");'
#         f'        element.style.cssText = "height:50px;";'
#         f"        document.body.append(element);"
#         f"        count += 1;"
#         f"    }}"
#         f"    if (!window.pageYOffset) {{"
#         f'        let topelemnt_ = document.createElement("div");'
#         f'        topelemnt_.style.cssText = "height:25px;";'
#         f"        document.body.prepend(topelemnt_);"
#         f"        window.scrollTo(0, 25);"
#         f"        up_count += 1;"
#         f"    }}"
#         f"    if (up_count > 3) {{"
#         f"        console.log(-1);"
#         f'        document.removeEventListener("scroll", scrolling);'
#         f"        return;"
#         f"    }}"
#         f"    if (count > 3) {{"
#         f'        document.removeEventListener("scroll", scrolling);'
#         f"        console.log(1);"
#         f"        return;"
#         f"    }}"
#         f"}});"
#     )

#     self.insert_script(script, "scroll_behavior")
#     self.inserted_script = True

# def set_font_size(self, size: int):
#     self.set_settings("font_size", size)
#     self.settings().setFontSize(QWebEngineSettings.FontSize.MinimumFontSize, size)

# def set_settings(self, key: str, value: str | int):
#     self.settings_[key] = value

# def set_background_color(self, color: str | QColor):
#     self.set_settings("background_color", color)
#     self.page().setBackgroundColor(color)

# def insert_web_view_css(self, css: str):
#     script = f'(function() {{ css = document.createElement("style"); css.type = "text/css"; document.head.appendChild(css); css.innerText = "{css}";}})()'
#     self.insert_script(script, "style")

# def insert_script(self, script, name):
#     script_ = QWebEngineScript()

#     self.page().runJavaScript(
#         script, QWebEngineScript.ScriptWorldId.ApplicationWorld
#     )
#     script_.setName(name)
#     script_.setSourceCode(script)
#     script_.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
#     script_.setRunsOnSubFrames(True)
#     script_.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)

#     self.page().scripts().insert(script_)

#     return script_

# def scroll_position_changed(self, height):
#     self.scroll_height = height

# def scroll_to(self, pos):
#     # SET SCROLL POS
#     self.queue_func(lambda: self.page().runJavaScript(f"window.scrollTo(0, {pos})"))


# def wheelEvent(self, event: QWheelEvent) -> None:
#     if not self.has_scrollbar:
#         delta = event.angleDelta().y()
#         if delta > 0:
#             # scrolling up
#             self.change_chapter(-1)
#         elif delta < 0:
#             # scrolling down
#             self.change_chapter(1)
#     return super().wheelEvent(event)

# def load_book(self) -> None:
#     """
#     Initialize epub file
#     """
#     logger.info("Loading Book")

#     handle = BookHandler(self.book_path, self.temp_dir, self.database)
#     book_found, toc, content = handle.read_saved_book()

#     # print(content)

#     logger.info("Done Parsing Book")

#     self.this_book = book_found

#     self.this_book["content"] = content
#     self.this_book["cover"] = base64.b64decode(book_found["cover"])

#     logger.info("Inserting content and cover into book")

# INITIALIZE BOOK WITH PREVIOUS SETTTINGS
# SET SCROLL POS

# logger.info("Inserting previous settings")
# self.scroll_y = None
# if "scroll_position" in self.this_book:
#     # self.parent().
#     self.scroll_y = self.this_book["scroll_position"]

# CHECK IF WE HAVE A RECORDED POS
# if len(self.this_book["position"]) == 0:
# self.set_content(0)

# else:
#     # SET CHAPTER POS
#     self.set_content(int(self.this_book["position"]["current_chapter"]))
#     self.scroll_to(self.scroll_y)

# # SET RECORDED WINDOW SIZE
# if "window_size" in self.this_book:
#     w = int(self.this_book["window_size"]["width"])
#     h = int(self.this_book["window_size"]["height"])

#     self.parent().resize(w, h)
# else:
#     w, h = 600, 900
#     self.parent().resize(w, h)

# logger.info("Done Inserting previous settings")
# self.has_scrollbar = True

# self.loadStarted.connect(
#     lambda: self.scroll_webpage_behavior(self.web_width, self.web_height)
# )
