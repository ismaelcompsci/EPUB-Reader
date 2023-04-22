from queue import Queue


from PyQt5.QtCore import QEvent, QObject
from PyQt5.QtGui import QKeyEvent, QMouseEvent, QWheelEvent
from PyQt5.QtWebEngineCore import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QWidget


class Page(QWebEnginePage):
    """
    Page for WebEnginView
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        print(f"{source_id}:{linenumber}: {msg}")

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)


class BookWebView(QWebEngineView):
    """
    Displays html from book
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self._page = Page(self)
        self.setPage(self._page)

        self.queue = Queue()

        self.loadFinished.connect(self.load_finished)
        self.loadStarted.connect(self.load_started)

        self.loading = False

        self._child_widget = None
        self.installEventFilter(self)

        self.web_width, self.web_height = self.size().width(), self.size().height()

    def load_finished(self, ok):
        self.web_width, self.web_height = self.size().width(), self.size().height()
        if ok:
            self.loading = False

        while not self.queue.empty():
            self.queue.get()()

    def load_started(self):
        self.loading = True
        self.web_width, self.web_height = self.size().width(), self.size().height()

    def queue_func(self, funciton):
        self.queue.put(funciton)

    def run_func(self, function):
        if not self.loading:
            function()

    def setHtml(self, html: str, baseUrl) -> None:
        try:
            self.focusProxy().installEventFilter(self)
        except AttributeError as e:
            print(e)
            pass
        return super().setHtml(html, baseUrl)

    def eventFilter(self, source: QObject, event: QEvent):
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
