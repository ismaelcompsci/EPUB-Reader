import sys
import ctypes
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from epub_reader.app.main_window import MainWindow


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv + ["--disable-web-security", "--no-sandbox"])
    w = MainWindow()
    w.setWindowIcon(QIcon(":reader/images/book.svg"))
    w.show()
    app.exec()


if __name__ == "__main__":
    if sys.platform == "win32":
        id = "epub-reader.library.v1.0.0"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id)

    sys.exit(main())
