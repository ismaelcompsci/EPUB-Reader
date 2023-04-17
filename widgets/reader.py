from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qframelesswindow import FramelessWindow
from tinydb import TinyDB
from .book_view import BookViewer
from .titlebars import BookSettingsWidget, BookTitleBar


class ReaderWindow(FramelessWindow):
    """
    Main view for reading books
    """

    def __init__(
        self,
        book_path: str,
        temp_dir: str,
        file_md5: str,
        metadata: str,
        database: TinyDB,
        parent: QWidget,
    ):
        super().__init__()

        self._parent = parent

        self.book_path = book_path
        self.temp_dir = temp_dir
        self.file_md5 = file_md5
        self.metadata = metadata
        self.database = database

        self.parent_bg_color = self._parent.palette().color(QPalette.ColorRole.Window)
        self.parent_color = self._parent.palette().color(QPalette.ColorRole.Text)

        self.init_ui()

        # RESIZE GRIPS qwebengineview resize not working -> solution
        # https://stackoverflow.com/a/62812752
        self.gripSize = 14
        self.grips = []

        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            grip.setStyleSheet("""background-color: transparent""")
            self.grips.append(grip)

    def init_ui(self):
        """
        Makes layout
        """

        self.v_layout = QVBoxLayout()
        self.v_layout.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.book_view = BookViewer(
            self,
            self.book_path,
            self.temp_dir,
            self.file_md5,
            self.database,
            self.metadata,
        )

        self.book_view.show()
        self.book_view.load_book()

        self.v_layout.addWidget(self.book_view)

        self.settings_widget = BookSettingsWidget()
        self.settings_widget.font_size.valueChanged.connect(
            self.book_view.set_font_size
        )

        self.setLayout(self.v_layout)

        self.setTitleBar(BookTitleBar(self, self.book_view.this_book["cover"]))
        self.titleBar.raise_()

        self.book_view.set_background_color(self.parent_bg_color)
        r, g, b, a = tuple(map(str, self.parent_color.getRgb()))
        self.book_view.insert_web_view_css(f"body {{color: rgba({r}, {g}, {b}, {a})}}")

    def settings_button_clicked(self):
        if self.settings_widget.isHidden():
            self.settings_widget.show()
        else:
            self.settings_widget.hide()

    def next_chapter(self) -> None:
        """
        Next chapter
        """
        self.book_view.change_chapter(1)

    def back_chapter(self) -> None:
        """
        Previous chapter
        """
        self.book_view.change_chapter(-1)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """ADDS RESIZEABLE WINDOW EVENT"""
        super(ReaderWindow, self).resizeEvent(event)
        rect = self.rect()
        # top left grip doesn't need to be moved...
        # top right
        self.grips[1].move(rect.right() - self.gripSize, 0)
        # bottom right
        self.grips[2].move(
            rect.right() - self.gripSize + 1, rect.bottom() + 1 - self.gripSize
        )
        # bottom left
        self.grips[3].move(0, rect.bottom() - self.gripSize + 1)

    def closeEvent(self, event) -> None:
        # WINDOW SIZE
        size = str(self.size().toTuple()).replace("(", "").replace(")", "").split(",")
        size[1] = size[1].replace(" ", "")

        w, h = size

        self.book_view.this_book["window_size"] = {}
        self.book_view.this_book["window_size"]["width"] = w
        self.book_view.this_book["window_size"]["height"] = h

        # SCROLL POSITION
        try:
            y = self.book_view.scroll_height.y()
        except AttributeError:
            y = 0

        self.book_view.this_book["scroll_position"] = y

        # STYLE
        # self.book_view.this_book["style"] = self.book_view.style_

        # print(self.content_view.this_book["style"])

        # SAVING TO FILE
        self.book_view.save_book_data()
        self.deleteLater()
        return super().closeEvent(event)
