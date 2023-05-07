# This file is a part of Lector, a Qt based ebook reader
# Copyright (C) 2017-2019 BasioMeusPuga

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO
# See if inserting chapters not in the toc.ncx can be avoided
# Account for stylesheets... eventually
"""https://github.com/BasioMeusPuga/Lector/blob/master/lector/readers/read_epub.py"""

import os
import zipfile
import logging
import collections
from urllib.parse import unquote

import xmltodict

# from PyQt5 import QtGui
# from PyQt5.QtGui import QTextDocument
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

img_css = """
max-width: 100%;
max-height: 100vh;
width: auto;
margin: auto;
"""

# ADD FILE LIST TO TOC TOO
#


class EPUB:
    def __init__(self, book_filename, temp_dir, extract_path):
        self.book_filename = book_filename
        self.temp_dir = temp_dir
        self.extract_path = extract_path

        self.zip_file = None
        self.file_list = None
        self.opf_dict = None
        self.cover_image_name = None
        self.split_chapters = {}

        self.metadata = None
        self.content = []

        self.generate_references()

    def generate_references(self):
        try:
            self.zip_file = zipfile.ZipFile(
                self.book_filename, mode="r", allowZip64=True
            )
        except zipfile.BadZipFile:
            return

        self.file_list = self.zip_file.namelist()

        # Book structure relies on parsing the .opf file
        # in the book. Now that might be the usual content.opf
        # or package.opf or it might be named after your favorite
        # eldritch abomination. The point is we have to check
        # the container.xml
        container = self.find_file("container.xml")

        if container:
            container_xml = self.zip_file.read(container)
            container_dict = xmltodict.parse(container_xml)
            # print(container_dict)
            packagefile = container_dict["container"]["rootfiles"]["rootfile"][
                "@full-path"
            ]

        else:
            presumptive_names = ("content.opf", "package.opf", "volume.opf")
            for i in presumptive_names:
                # print(f"persumtive_name: {i}")
                packagefile = self.find_file(i)
                if packagefile:
                    logger.info("Using presumptive package file: " + self.book_filename)
                    break

        try:
            packagefile_data = self.zip_file.read(packagefile)
        except KeyError:
            presumptive_names = ("content.opf", "package.opf", "volume.opf")
            for i in presumptive_names:
                # print(f"persumtive_name: {i}")
                packagefile = self.find_file(i)
                if packagefile:
                    logger.info("Using presumptive package file: " + self.book_filename)
                    packagefile_data = self.zip_file.read(packagefile)
                    break

        self.opf_dict = xmltodict.parse(packagefile_data)

    def find_file(self, filename):
        # Get rid of special characters
        filename = unquote(filename)
        # print(f"find_file : ", filename)

        # First, look for the file in the root of the book
        if filename in self.file_list:
            return filename

        # Then search for it elsewhere
        else:
            # print(filename)
            file_basename = os.path.basename(filename)
            # print(file_basename)
            # print(self.file_list)
            for i in self.file_list:
                if os.path.basename(i) == file_basename:
                    return i

        # If the file isn't found
        logger.warning(filename + " not found in " + self.book_filename)
        return False

    def generate_metadata(self):
        book_metadata = self.opf_dict["package"]["metadata"]

        def flattener(this_object):
            if isinstance(this_object, dict):
                return this_object["#text"]

            if isinstance(this_object, list):
                if isinstance(this_object[0], dict):
                    return this_object[0]["#text"]
                else:
                    return this_object[0]

            if isinstance(this_object, str):
                return this_object

        # There are no exception types specified below
        # This is on purpose and makes me long for the days
        # of simpler, happier things.

        # Book title
        try:
            title = flattener(book_metadata["dc:title"])
        except:
            logger.warning("Title not found: " + self.book_filename)
            title = os.path.splitext(os.path.basename(self.book_filename))[0]

        # Book author
        try:
            author = flattener(book_metadata["dc:creator"])
        except:
            logger.warning("Author not found: " + self.book_filename)
            author = "Unknown"

        # Book year
        try:
            year = int(flattener(book_metadata["dc:date"])[:4])
        except:
            logger.warning("Year not found: " + self.book_filename)
            year = 9999

        # Book isbn
        # Both one and multiple schema
        isbn = None
        try:
            scheme = book_metadata["dc:identifier"]["@opf:scheme"].lower()
            if scheme.lower() == "isbn":
                isbn = book_metadata["dc:identifier"]["#text"]

        except (TypeError, KeyError):
            try:
                for i in book_metadata["dc:identifier"]:
                    if i["@opf:scheme"].lower() == "isbn":
                        isbn = i["#text"]
                    break
            except:
                logger.warning("ISBN not found: " + self.book_filename)

        # Book tags
        try:
            tags = book_metadata["dc:subject"]
            if isinstance(tags, str):
                tags = [tags]
        except:
            tags = []

        # Book cover
        cover = self.generate_book_cover()

        # Named tuple? Named tuple.
        Metadata = collections.namedtuple(
            "Metadata", ["title", "author", "year", "isbn", "tags", "cover"]
        )
        self.metadata = Metadata(title, author, year, isbn, tags, cover)

    def generate_book_cover(self):
        # This is separate because the book cover needs to
        # be found and extracted both during addition / reading
        book_cover = None

        try:
            cover_image = [
                i["@href"]
                for i in self.opf_dict["package"]["manifest"]["item"]
                if i["@media-type"].split("/")[0] == "image" and "cover" in i["@id"]
            ][0]
            book_cover = self.zip_file.read(self.find_file(cover_image))
        except:
            logger.warning("Cover not found in opf: " + self.book_filename)

        # Find book cover the hard way
        if not book_cover:
            biggest_image_size = 0
            cover_image = None
            for j in self.zip_file.filelist:
                if os.path.splitext(j.filename)[1] in [".jpg", ".jpeg", ".png", ".gif"]:
                    if j.file_size > biggest_image_size:
                        cover_image = j.filename
                        biggest_image_size = j.file_size

            if cover_image:
                book_cover = self.zip_file.read(self.find_file(cover_image))

        if not book_cover:
            self.cover_image_name = ""
            logger.warning("Cover not found: " + self.book_filename)
        else:
            self.cover_image_name = os.path.splitext(os.path.basename(cover_image))[0]

        return book_cover
