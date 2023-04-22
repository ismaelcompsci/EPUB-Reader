# coding:utf-8
from enum import Enum


from qfluentwidgets import Theme, StyleSheetBase, qconfig


class StyleSheet(StyleSheetBase, Enum):
    LIBRARY_INTERFACE = "library_interface"
    MAIN_WINDOW = "main_window"
    BOOK_INTERFACE = "book_interface"
    SETTING_INTERFACE = "setting_interface"
    BOOK_WINDOW_INTERFACE = "book_window_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        print(f":/reader/{theme.value.lower()}/{self.value}.qss")
        return f":/reader/{theme.value.lower()}/{self.value}.qss"
