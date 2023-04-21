# coding:utf-8
import sys
import resource.resource_rc

from helpers.style_sheet import StyleSheet
from PyQt5.QtCore import QEasingCurve, Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QWidget,
)
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import (
    NavigationInterface,
    NavigationItemPosition,
    PopUpAniStackedWidget,
)
from qframelesswindow import FramelessWindow
from widgets.libraryinterface import LibraryInterface
from widgets.reader import ReaderInterface
from widgets.settingsinterface import SettingInterface
from widgets.bars import CustomTitleBar


class StackedWidget(QFrame):
    """Stacked widget"""

    currentWidgetChanged = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(
            lambda i: self.currentWidgetChanged.emit(self.view.widget(i))
        )

    def addWidget(self, widget):
        """add widget to view"""
        self.view.addWidget(widget)

    def setCurrentWidget(self, widget: QWidget, popOut=False):
        try:
            widget.verticalScrollBar().setValue(0)
        except AttributeError:
            pass

        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class Window(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))

        self.emptyLibrary = True

        self.hBoxLayout = QHBoxLayout(self)
        self.widgetLayout = QHBoxLayout()

        self.stackWidget = StackedWidget(self)
        self.navigationInterface = NavigationInterface(self, True, True)

        # create sub interface
        self.libraryInterface = LibraryInterface("Library", "libraryInterface", self)
        self.settingInterface = SettingInterface(self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)
        self.titleBar.raise_()

    def initNavigation(self):
        # Library View
        self.addSubInterface(
            self.libraryInterface,
            "libraryInterface",
            FIF.BOOK_SHELF,
            "Library",
            NavigationItemPosition.TOP,
        )

        self.navigationInterface.addSeparator()

        self.addSubInterface(
            self.settingInterface,
            "settingInterface",
            FIF.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )

        # Default route
        self.navigationInterface.setDefaultRouteKey(self.libraryInterface.objectName())

        # Update current widget
        self.stackWidget.currentWidgetChanged.connect(
            lambda: self.navigationInterface.setCurrentItem(w.objectName())
        )
        # Set Library as home
        self.navigationInterface.setCurrentItem(self.libraryInterface.objectName())
        self.stackWidget.setCurrentIndex(0)

        # Open book signal
        self.libraryInterface.libraryView.openSignal.connect(self.openBook)

    def initWindow(self):
        self.resize(1084, 680)
        self.setMinimumWidth(600)
        self.setWindowTitle("EPUB-Reader")
        self.titleBar.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        StyleSheet.MAIN_WINDOW.apply(self)
        # setTheme(Theme.AUTO)

    def openBook(self, metadata):
        # Create Book View
        bookInterface = ReaderInterface(self, metadata)

        self.addSubInterface(
            bookInterface,
            metadata["hash"],
            FIF.VIDEO,
            metadata["title"],
            NavigationItemPosition.TOP,
        )

        self.switchTo(bookInterface, True)
        self.navigationInterface.setCurrentItem(metadata["hash"])

    def addSubInterface(
        self,
        interface: QWidget,
        objectName: str,
        icon,
        text: str,
        position=NavigationItemPosition.SCROLL,
    ):
        interface.setObjectName(objectName)
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=objectName,
            icon=icon,
            text=text,
            onClick=lambda t: self.switchTo(interface, t),
            position=position,
        )

    def switchTo(self, widget, triggerByUser=True):
        self.stackWidget.setCurrentWidget(widget, not triggerByUser)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())


if __name__ == "__main__":
    app = QApplication(sys.argv + ["", "--no-sandbox"])
    w = Window()
    w.show()
    app.exec()
