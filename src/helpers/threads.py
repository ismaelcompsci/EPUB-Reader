import os
import shutil

from config.config import BOOK_COPIES_DIR, EXTRACTED_EPUB_DIR, Books
from PyQt5.QtCore import QThread, pyqtSignal
from utils.bookhandler import BookHandler

FILENAME_INVALID_CHARACTERS = '<>:"|?*'


class BackGroundBookAddition(QThread):
    bookAdded = pyqtSignal(dict)
    badBookAdded = pyqtSignal(object)

    def __init__(self, files, main_window, parent=None):
        super().__init__(parent)

        self.files = files[0]
        self.main_window = main_window

        self.library_ref = parent

    def run(self):
        for file in self.files:
            # SAVE THE BOOK
            handle = BookHandler(file, EXTRACTED_EPUB_DIR, Books)
            read_ = handle.read_book()

            if isinstance(read_, tuple):
                # ALREADY IN LIBRARY
                if read_[1]:
                    self.badBookAdded.emit((file, 303))
                    continue

                # PARSE ERROR
                if read_[0]:
                    self.badBookAdded.emit(file)
                    continue

            title = handle.this_book["title"].replace(FILENAME_INVALID_CHARACTERS, "_")
            author = handle.this_book["author"].replace(
                FILENAME_INVALID_CHARACTERS, "_"
            )

            new_basename = f"{title}-{author}"

            # NEW FULL PATH TO COPY DIRECTORY
            new_path = os.path.join(BOOK_COPIES_DIR, new_basename) + ".epub"

            # ONLY COPY IF GOOD READ_
            # COPY THE FILE TO NEW LOCATION
            try:
                new_file_path = shutil.copy(file, new_path)
            except shutil.SameFileError:
                new_file_path = new_path

            metadata = handle.save_book(new_file_path)
            self.bookAdded.emit(metadata)


class BackGroundBookDeletion(QThread):
    def __init__(self, metadata):
        super().__init__()

        self.metadata = metadata

    def run(self):
        file = self.metadata["path"]
        handle = BookHandler(file, EXTRACTED_EPUB_DIR, Books)
        handle.delete_book()
