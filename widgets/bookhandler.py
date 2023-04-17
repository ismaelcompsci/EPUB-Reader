import base64
import copy
import datetime
import logging
import os
import shutil
from tinydb import Query, TinyDB, where

from utils.utils import get_file_md5_hash, resize_image
from epub.epub import ParseEPUB

logger = logging.getLogger(__name__)


class BookHandler:
    """
    Adds Book to database
    """

    def __init__(self, book_path: str, temp_dir: str, database: TinyDB):
        self.db = database

        self.book_path = book_path
        self.temp_dir = temp_dir

    def hash_book(self) -> str:
        return get_file_md5_hash(self.book_path)

    def delete_book(self):
        md5_ = self.hash_book()

        # REMOVE FROM DATABASE
        self.db.remove(where("hash") == md5_)

        # REMOVE FROM TEMP
        book_dir = os.path.join(self.temp_dir, md5_)
        shutil.rmtree(book_dir)

        # REMOVE COVER
        cover_path = (
            os.path.join(self.temp_dir, os.path.basename(self.book_path)) + " - cover"
        )
        if os.path.isfile(cover_path):
            os.remove(cover_path)

        return

    def read_book(self):
        """
        Initialize epub file
        """
        Check = Query()
        self.md5_ = self.hash_book()

        # CHECK IF BOOK IS IN DB
        book = self.db.get(Check.hash == self.md5_)
        if book:
            return False

        # BOOK DATA
        parsed_book = ParseEPUB(self.book_path, self.temp_dir, self.md5_)
        parsed_book.read_book()

        metadata = parsed_book.generate_metadata()

        try:
            (
                toc,
                content,
                images_only,
            ) = parsed_book.generate_content()  # FOR READING

        except Exception as e:
            shutil.rmtree(os.path.join(self.temp_dir, self.md5_))
            this_error = f"Content generation error: {self.book_path}"
            print(this_error + f" {type(e).__name__} Arguments: {e.args}")
            return False

        this_book = {}

        cover_image = resize_image(metadata.cover)

        this_book = {
            "hash": self.md5_,
            "path": self.book_path,
            "position": {},
            "bookmarks": None,
            "toc": toc,
            "content": content,
            "cover": cover_image,
            "title": metadata.title,
            "author": metadata[1],
            "year": metadata[2],
            "isbn": metadata[3],
            "tags": metadata[4],
            "date_added": datetime.datetime.now().timestamp() * 1000,
        }

        # logger.info(f" DONE READDING BOOK: {metadata.title}")

        self.this_book = this_book

        return True

    def read_saved_book(self) -> tuple:
        """
        Reads book in database
        """

        logger.info("Reading book from database")

        Book = Query()
        self.file_md5 = self.hash_book()

        book_found = self.db.get(Book.hash == self.file_md5)

        book = ParseEPUB(self.book_path, self.temp_dir, self.file_md5)
        book.read_book()
        toc, content, images_only = book.generate_content()

        return (book_found, toc, content)

    def save_book(self) -> None:
        """
        Save to database
        """
        Book = Query()
        # CHECK IF BOOK ALREADY EXISTS
        book = self.db.get(Book.hash == self.md5_)
        if book:
            return

        new_metadata = copy.deepcopy(self.this_book)
        new_metadata.pop("content")

        # ENCODED IMAGE
        image = base64.b64encode(new_metadata["cover"]).decode("utf-8")
        # DECODE -> base64.b64decode(encoded_image)

        new_metadata["cover"] = image

        self.db.insert(new_metadata)
