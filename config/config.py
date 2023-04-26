import os
from qfluentwidgets import (
    QConfig,
    ConfigItem,
    FolderValidator,
    qconfig,
)
from platformdirs import user_data_dir
from tinydb import TinyDB


appname = "EPUB-Reader"
appautor = "Ismael Olvera"


def create_or_check(path: str | list) -> str | list:
    if isinstance(path, str):
        if not os.path.exists(path):
            os.makedirs(path)

    if isinstance(path, list):
        for dir_ in path:
            if not os.path.exists(dir_):
                os.makedirs(dir_)

    return path


# STORES BOOK STUFF
DATA_DIR = user_data_dir(appname)

# STORES EXTRACTED EPUB FILES
EXTRACTED_EPUB_DIR = os.path.join(DATA_DIR, "data")

# DATABASE DIR
DATABASE_DIR = os.path.join(DATA_DIR, "db")

# STORES COPIED BOOK
BOOK_COPIES_DIR = os.path.join(DATA_DIR, "Books")

# GUI CONFIGN
GUI_CONFIG_DIR = os.path.join(DATA_DIR, "config")

# CREATE THE DIRS
create_or_check(
    [DATA_DIR, DATABASE_DIR, BOOK_COPIES_DIR, EXTRACTED_EPUB_DIR, GUI_CONFIG_DIR]
)


class Config(QConfig):
    tempFolder = ConfigItem("Folders", "temp", GUI_CONFIG_DIR, FolderValidator())

    fontSize = ConfigItem("Reader", "fontsize", 24)


cfg = Config()


qconfig.load(GUI_CONFIG_DIR + "\\config.json", cfg)

db_ = TinyDB(DATABASE_DIR + "\\Books.json")
Books = db_.table("Books")
Settings = db_.table("Settings")
