from platformdirs import *
import os

from tinydb import TinyDB
from utils.utils import create_or_check

appname = "EPUB-Reader"
appauthor = "Ismael Olvera"

# STORES EXTRACTED EPUBS AND DATABASE
DATA_DIR = user_data_dir(appname)

# DATABASE DIR
DATABASE_DIR = create_or_check(os.path.join(DATA_DIR, "db"))
TEMPDIR = create_or_check(DATA_DIR)

# CREATE DATABASE
_db = TinyDB(DATABASE_DIR + "\\Books.json")
