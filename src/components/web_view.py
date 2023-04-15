import json
import sys
from queue import Queue

import PySide6
from PySide6.QtCore import QEvent, QObject, QPoint
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent, QAction
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QWidget, QMenu


class Page(QWebEnginePage):
    """
    WebEngineView Page
    """

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        print(f"{source_id}:{linenumber}: {msg}")

        if msg:
            self.parent().handle_(msg)

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class WebView(QWebEngineView):
    """
    https://doc.qt.io/qtforpython/PySide6/QtWebEngineWidgets/QWebEngineView.html
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._page = Page(self)
        self.setPage(self._page)
        self.queue = Queue()
        self.loadFinished.connect(self.on_load_finished)
        self.loadStarted.connect(self.load_started)

        self.loading = False

        self._childWidget = None
        self.installEventFilter(self)

    def on_load_finished(self) -> None:
        """
        Runs function after view is done loading.
        """
        self.loading = False

        while not self.queue.empty():
            self.queue.get()()

    def load_started(self) -> None:
        self.loading = True

    def queue_func(self, function) -> None:
        """
        Queue function to run when view is done loading
        """
        self.queue.put(function)

    def run_func(self, function) -> None:
        if not self.loading:
            function()

    def eventFilter(self, source: QObject, event: QEvent):
        """
        MAKES MOUSE EVENT HANDLERS WORK
        """

        if (
            event.type() == QEvent.Type.ChildAdded
            and source is self
            and event.child().isWidgetType()
        ):
            self._childWidget = event.child()
            self._childWidget.installEventFilter(self)
        # MOUSE SCROLL
        elif isinstance(event, QWheelEvent) and source is self._childWidget:
            self.wheelEvent(event)

        # MOUSE PRESS
        elif isinstance(event, QMouseEvent) and source is self._childWidget:
            if event.type() == QEvent.Type.MouseButtonPress:
                # print(event.pos())
                self.mousePressEvent(event)
            if event.type() == QEvent.Type.MouseButtonRelease:
                self.mouseReleaseEvent(event)

        # KEY PRESS
        elif isinstance(event, QKeyEvent) and source is self._childWidget:
            if event.type() == QEvent.Type.KeyPress:
                self.keyPressEvent(event)

        return super().eventFilter(source, event)

    def wheelEvent(self, event: QWheelEvent) -> None:
        return super().wheelEvent(event)
