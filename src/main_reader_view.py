import os
import qdarkstyle

import PySide6
from components.book_view import EReader
from components.custom_widgets import MyTitleBar, SettingsWidget
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qframelesswindow import FramelessWindow
from tinydb import Query, TinyDB


class EWindow(FramelessWindow):
    """
    Main view for reading books
    """

    def __init__(
        self,
        filepath: str,
        temp: str,
        file_md5: str,
        full_metadata: dict,
        database: TinyDB,
        parent: QWidget,
    ) -> None:
        super().__init__()

        self._parent = parent

        self.filePath = filepath
        self.temp = temp
        self.file_md5 = file_md5
        self.metadata = full_metadata

        self.db = database

        self.parent_bg_color = self._parent.palette().color(QPalette.ColorRole.Window)
        self.parent_color = self._parent.palette().color(QPalette.ColorRole.Text)

        self.set_layout()  # SET LAYOUT

        # RESIZE GRIPS qwebengineview resize not working -> solution
        # https://stackoverflow.com/a/62812752
        self.gripSize = 14
        self.grips = []

        for i in range(4):
            grip = QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            grip.setStyleSheet("""background-color: transparent""")
            self.grips.append(grip)

    # SET LAYOUT OF FRAMLESSWINDOW
    def set_layout(self) -> None:
        """
        Makes Ui layout
        """
        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(0, self.titleBar.height(), 0, 0)

        self.content_view = EReader(
            self,
            self.filePath,
            self.temp,
            self.file_md5,
            self.db,
            self.metadata,
        )

        self.content_view.show()
        self.content_view.load_book()

        self.layout_.addWidget(self.content_view)

        # SETTINGS TOGGLE
        self.settings_widget = SettingsWidget()
        # FONT SIZE
        self.settings_widget.font_size.valueChanged.connect(
            self.content_view.set_font_size
        )

        # # BACKGROUND COLOR
        # self.settings_widget.bg_dark.toggled.connect(
        #     lambda: self.content_view.bg_buttons_toggled(self.settings_widget.bg_dark)
        # )
        # self.settings_widget.bg_light.toggled.connect(
        #     lambda: self.content_view.bg_buttons_toggled(self.settings_widget.bg_light)
        # )

        self.setLayout(self.layout_)
        self.setTitleBar(MyTitleBar(self, self.content_view.this_book["cover"]))
        self.titleBar.raise_()

        self.content_view.set_background_color(self.parent_bg_color)
        r, g, b, a = tuple(map(str, self.parent_color.getRgb()))
        self.content_view.web_view_css(f"body {{color: rgba({r}, {g}, {b}, {a})}}")

    def settings_button_clicked(self) -> None:
        """
        Hides or shows settings widget
        """
        if self.settings_widget.isHidden():
            self.settings_widget.show()
        else:
            self.settings_widget.hide()

        # self.layout_.addWidget(self.content_view)

    def next_chapter(self) -> None:
        """
        Next chapter
        """
        self.content_view.change_chapter(1)

    def back_chapter(self) -> None:
        """
        Previous chapter
        """
        self.content_view.change_chapter(-1)

    def resizeEvent(self, event: QResizeEvent) -> None:
        """ADDS RESIZEABLE WINDOW EVENT"""
        super(EWindow, self).resizeEvent(event)
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

    def closeEvent(self, event: PySide6.QtGui.QCloseEvent) -> None:
        # WINDOW SIZE
        size = str(self.size().toTuple()).replace("(", "").replace(")", "").split(",")
        size[1] = size[1].replace(" ", "")

        w, h = size

        self.content_view.this_book["window_size"] = {}
        self.content_view.this_book["window_size"]["width"] = w
        self.content_view.this_book["window_size"]["height"] = h

        # SCROLL POSITION
        try:
            y = self.content_view.scroll_height.y()
        except AttributeError:
            y = 0

        self.content_view.this_book["scroll_position"] = y

        # STYLE
        self.content_view.this_book["style"] = self.content_view.style_

        # print(self.content_view.this_book["style"])

        # SAVING TO FILE
        self.content_view.save_book_data()
        self.deleteLater()
        return super().closeEvent(event)
