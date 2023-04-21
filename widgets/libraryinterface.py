from PyQt5.QtCore import Qt, pyqtSignal

from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QWidget,
    QAction,
    QHBoxLayout,
)
from qfluentwidgets import (
    FlowLayout,
    SmoothScrollArea,
    SearchLineEdit,
    ScrollArea,
    RoundMenu,
)
from qfluentwidgets import FluentIcon as FIF
from .bars import LibraryToolBar

from .bookcard import BookCard, BookCover
from tinydb import Query, TinyDB

from helpers.style_sheet import StyleSheet
from helpers.threads import BackGroundBookAddition
from pytrie import SortedStringTrie as Trie

from config.config import DATABASE_DIR, Books


class LineEdit(SearchLineEdit):
    """Search line edit"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText(self.tr("Search Books"))
        self.setFixedWidth(304)
        self.textChanged.connect(self.search)


class LibraryScrollInterface(ScrollArea):
    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent=parent)

        self.view = QWidget(self)
        # self.toolbar = ToolBar
        self.vBoxLayout = QVBoxLayout(self.view)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # self.setViewportMargins(0, 32, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.vBoxLayout.setContentsMargins(36, 20, 36, 36)
        self.view.setObjectName("view")

        StyleSheet.LIBRARY_INTERFACE.apply(self)

    def scrollToCard(self, index: int):
        """scroll to example card"""
        w = self.vBoxLayout.itemAt(index).widget()
        self.verticalScrollBar().setValue(w.y())

    def resizeEvent(self, e):
        super().resizeEvent(e)


class LibraryInfoPanel(QFrame):
    """Book info panel"""

    def __init__(self, metadata=None, parent=None):
        super().__init__(parent=parent)
        if not metadata:
            return

        self.nameLabel = QLabel(metadata["title"], self)

        self.iconWidget = BookCover(metadata["cover"])
        self.iconNameTitleLabel = QLabel(metadata["title"], self)
        self.iconNameLabel = QLabel(metadata["author"], self)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(16, 20, 16, 20)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.vBoxLayout.addWidget(self.nameLabel)
        self.vBoxLayout.addSpacing(16)
        self.vBoxLayout.addWidget(self.iconWidget)
        self.vBoxLayout.addSpacing(45)
        self.vBoxLayout.addWidget(self.iconNameTitleLabel)
        self.vBoxLayout.addSpacing(5)
        self.vBoxLayout.addWidget(self.iconNameLabel)
        self.vBoxLayout.addSpacing(34)

        self.iconWidget.setFixedSize(150, 250)
        self.iconWidget.setScaledContents(True)

        self.nameLabel.setWordWrap(True)
        self.iconNameTitleLabel.setWordWrap(True)
        self.setFixedWidth(216)

        self.nameLabel.setObjectName("nameLabel")
        self.iconNameTitleLabel.setObjectName("subTitleLabel")

    def setIcon(self, metadata):
        if not metadata:
            return
        self.iconWidget.set_pixmap(metadata["cover"])
        self.nameLabel.setText(metadata["title"])
        self.iconNameLabel.setText(metadata["author"])
        self.iconNameTitleLabel.setText(metadata["title"])


# class


class LibraryCardView(QWidget):
    """
    Library gallery view
    """

    openSignal = pyqtSignal(dict)
    deleteSignal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.trie = Trie()
        self.emptyLibrary = True

        self.hBoxLayoutSearchAdd = QHBoxLayout()

        self.libraryLabel = QLabel("Library", self)
        self.searchLineEdit = LibraryToolBar(self)

        self.view = QFrame(self)
        self.scrollArea = SmoothScrollArea(self.view)
        self.scrollWidget = QWidget(self.scrollArea)
        # INFO PANEL

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout(self.view)
        self.flowLayout = FlowLayout(self.scrollWidget, isTight=False)

        self.cards = []
        self.books = []

        self.currentIndex = -1

        self.hasBooks = Books.get(doc_id=1)

        if self.hasBooks:
            self.emptyLibrary = False
        else:
            self.emptyLibrary = True

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setViewportMargins(0, 5, 0, 5)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        # self.vBoxLayout.setSpacing(12)
        self.vBoxLayout.addWidget(self.libraryLabel)
        self.vBoxLayout.addWidget(self.searchLineEdit)
        self.vBoxLayout.addLayout(self.hBoxLayoutSearchAdd)
        self.vBoxLayout.addWidget(self.view)

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.scrollArea)

        self.flowLayout.setVerticalSpacing(8)
        self.flowLayout.setHorizontalSpacing(8)
        # self.flowLayout.setContentsMargins(8, 3, 8, 8)

        self.__setQss()
        # self.searchLineEdit.clearSignal.connect(self.showAllIcons)
        # self.searchLineEdit.searchSignal.connect(self.search)

        if self.emptyLibrary == False:
            self.genLibrary()
            self.makeInfopanel()

    def makeInfopanel(self):
        if len(self.books) == 0:
            self.infoPanel = None
        else:
            self.infoPanel = LibraryInfoPanel(self.books[0], self)
            self.hBoxLayout.addWidget(self.infoPanel, 0, Qt.AlignmentFlag.AlignRight)

    def genLibrary(self):
        self.cards = []
        self.books = []
        self.flowLayout.removeAllWidgets()

        self.books_db = Books.all()
        self.getLibraryBooks()

    def getLibraryBooks(self):
        i = 0

        for book in self.books_db:
            self.addLibraryItem(book)
            self.trie[book["title"].lower()] = i
            i += 1

    def addLibraryItem(self, book_data):
        book = BookCard(book_data, self)
        book.clicked.connect(self.setSelectedBook)

        self.cards.append(book)
        self.books.append(book_data)
        self.flowLayout.addWidget(book)

    def setSelectedBook(self, book_data):
        index = self.books.index(book_data)

        if self.currentIndex >= 0:
            self.cards[self.currentIndex].setSelected(False)

        self.currentIndex = index
        self.cards[index].setSelected(True)

        self.infoPanel.setIcon(book_data)

    def __setQss(self):
        self.view.setObjectName("iconView")
        self.scrollWidget.setObjectName("scrollWidget")
        self.libraryLabel.setObjectName("iconLibraryLabel")

        StyleSheet.BOOK_INTERFACE.apply(self)

        if self.currentIndex >= 0:
            self.cards[self.currentIndex].setSelected(True, True)

    def search(self, key_word: str):
        if not self.trie.keys():
            return

        # ITEMS ASSOCIATED WITH KEYS PREFIXED BY PREFIX
        hits = self.trie.items(prefix=key_word)

        # INDEX IN CARD LIST
        indexs = {i[1] for i in hits}

        # ONLY SET VISIBLE IF i IN INDEXES
        for i in range(len(self.cards)):
            self.cards[i].setVisible(i in indexs)

    def showAllIcons(self):
        for card in self.cards:
            card.show()

    def contextMenuEvent(self, event) -> None:
        bookSelectedData = self.cards[self.currentIndex].metadata

        menu = RoundMenu(parent=self)

        # Actions
        openAction = QAction(FIF.LINK.icon(), "Open")
        deleteAction = QAction(FIF.DELETE.icon(), "Delete")

        menu.addAction(openAction)
        menu.addAction(deleteAction)

        openAction.triggered.connect(lambda: self.openSignal.emit(bookSelectedData))
        deleteAction.triggered.connect(lambda: print("what"))

        menu.exec(event.globalPos(), ani=True)

    def mouseDoubleClickEvent(self, event) -> None:
        widget = self.childAt(event.pos())

        if isinstance(widget, BookCover) or isinstance(widget, BookCard):
            bookSelectedData = self.cards[self.currentIndex].metadata

            if widget:
                self.openSignal.emit(bookSelectedData)

        return


class LibraryInterface(LibraryScrollInterface):
    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(title, subtitle, parent)

        self.libraryView = LibraryCardView(self)
        self.vBoxLayout.addWidget(self.libraryView)

        self.libraryView.searchLineEdit.openFileDialog.connect(self.openFileDialog)

        self.setObjectName(subtitle)

    def openFileDialog(self):
        files = QFileDialog.getOpenFileNames(
            self,
            "Open EPUB",
            filter="EPUB Files (*.epub)",
        )

        self.thread_ = BackGroundBookAddition(files, self.parent(), self)
        self.thread_.bookAdded.connect(self.updateLibraryInterface)
        self.thread_.start()

    def updateLibraryInterface(self, metadata):
        self.libraryView.emptyLibrary = False
        self.libraryView.infoPanel.deleteLater()  # IS THIS OKAY? ???
        self.libraryView.makeInfopanel()
        self.libraryView.addLibraryItem(metadata)
