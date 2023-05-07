import sys

from PyQt5.QtCore import Qt
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
    w.show()
    app.exec()


if __name__ == "__main__":
    sys.exit(main())
