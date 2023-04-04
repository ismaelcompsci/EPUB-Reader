from queue import Queue
from PySide6.QtCore import QEvent
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWebEngineWidgets import QWebEngineView


class WebView(QWebEngineView):
    """
    https://doc.qt.io/qtforpython/PySide6/QtWebEngineWidgets/QWebEngineView.html
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.queue = Queue()
        self.loadFinished.connect(self.on_load_finished)

        self.loading = False

        self._childWidget = None
        self.installEventFilter(self)

    def on_load_finished(self):
        """
        Runs function after view is done loading.
        """

        while not self.queue.empty():
            self.queue.get()()

    def queue_func(self, function):
        """
        Queue function to run when view is done loading
        """
        self.queue.put(function)

    def eventFilter(self, source, event):
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
        elif isinstance(event, QMouseEvent) and source is self._childWidget:
            if event.type() == QEvent.Type.MouseButtonPress:
                # print(event.pos())
                self.mousePressEvent(event)
        elif isinstance(event, QKeyEvent) and source is self._childWidget:
            if event.type() == QEvent.Type.KeyPress:
                self.keyPressEvent(event)

        return super().eventFilter(source, event)
