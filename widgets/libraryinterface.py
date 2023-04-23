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
from tinydb import Query, TinyDB, where

from helpers.style_sheet import StyleSheet
from helpers.threads import BackGroundBookAddition, BackGroundBookDeletion
from pytrie import SortedStringTrie as Trie

from config.config import DATABASE_DIR, Books


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

        self.nameLabel = QLabel(self)

        self.iconWidget = BookCover(":reader/images/placeholder.png")
        self.iconNameTitleLabel = QLabel("", self)
        self.iconNameLabel = QLabel("", self)

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
        self.trie_len = 0

        self.hBoxLayoutSearchAdd = QHBoxLayout()

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

        if len(Books):
            self.emptyLibrary = False
        else:
            self.emptyLibrary = True

        self.__initWidget()

    def __initWidget(self):
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setViewportMargins(0, 0, 0, 0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
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
        self.searchLineEdit.searchLine.searchSignal.connect(self.search)
        self.searchLineEdit.searchLine.clearSignal.connect(self.showAllIcons)

        if self.emptyLibrary == False:
            self.genLibrary()
        self.makeInfopanel()

    def makeInfopanel(self):
        if len(self.books) == 0:
            self.infoPanel = LibraryInfoPanel(None, self)
            self.hBoxLayout.addWidget(self.infoPanel, 0, Qt.AlignmentFlag.AlignRight)
        else:
            self.infoPanel = LibraryInfoPanel(self.books[0], self)
            self.hBoxLayout.addWidget(self.infoPanel, 0, Qt.AlignmentFlag.AlignRight)

    def genLibrary(self):
        self.cards = []
        self.books = []
        self.trie_len = 0
        self.flowLayout.takeAllWidgets()

        self.books_db = Books.all()
        self.getLibraryBooks()

    def getLibraryBooks(self):
        for book in self.books_db:
            self.addLibraryItem(book)

    def addLibraryItem(self, book_data):
        book = BookCard(book_data, self)
        book.clicked.connect(self.setSelectedBook)

        self.cards.append(book)
        self.books.append(book_data)
        self.flowLayout.addWidget(book)

        # Add Book to Trie
        self.trie[book_data["title"].lower()] = self.trie_len
        self.trie_len += 1

    def delLibraryItem(self, book_data):
        index = self.currentIndex

        card = self.cards.pop(index)
        book = self.books.pop(index)
        w = self.flowLayout.takeAt(index)

        if w:
            w.deleteLater()

        self.genLibrary()
        self.infoPanel.deleteLater()
        self.makeInfopanel()

        self.update()

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
        # self.libraryLabel.setObjectName("iconLibraryLabel")

        StyleSheet.BOOK_INTERFACE.apply(self)

        if self.currentIndex >= 0:
            self.cards[self.currentIndex].setSelected(True, True)

    def search(self, key_word: str):
        if not self.trie.keys():
            return

        key_word = key_word.lower()

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
        if len(self.cards) == 0:
            return
        bookSelectedData = self.cards[self.currentIndex].metadata

        menu = RoundMenu(parent=self)

        # Actions
        openAction = QAction(FIF.LINK.icon(), "Open")
        deleteAction = QAction(FIF.DELETE.icon(), "Delete")

        menu.addAction(openAction)
        menu.addAction(deleteAction)

        openAction.triggered.connect(lambda: self.openSignal.emit(bookSelectedData))
        deleteAction.triggered.connect(lambda: self.deleteSignal.emit(bookSelectedData))

        menu.exec(event.globalPos(), ani=True)

    def mouseDoubleClickEvent(self, event) -> None:
        if len(self.cards) == 0:
            return

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
        self.libraryView.deleteSignal.connect(self.deleteBook)

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

    def deleteBook(self, book_data):
        self.thread_ = BackGroundBookDeletion(book_data)
        self.thread_.finished.connect(
            lambda: self.updateLibraryInterface(book_data, True)
        )
        self.thread_.start()

    def updateLibraryInterface(self, metadata, delete=False):
        if delete:
            # DELETE BOOK FROM LIBRARY VIEW
            self.libraryView.delLibraryItem(metadata)

        else:
            self.libraryView.emptyLibrary = False
            # self.libraryView.infoPanel.deleteLater()
            # self.libraryView.makeInfopanel()
            self.libraryView.addLibraryItem(metadata)


# TODO
# MAKE NEW WINDOW POP UP FOR BOOK VIEW
# JUST BETTER
