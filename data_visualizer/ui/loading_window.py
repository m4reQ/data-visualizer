import typing as t

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow, QWidget

_UI_FILEPATH = './assets/uis/loading_window.ui'

class LoadingWindow(QMainWindow):
    @classmethod
    def open_blocking(cls, parent: QWidget, filepath: str) -> t.Self:
        win = cls(parent, filepath)
        win.setWindowModality(Qt.WindowModality.ApplicationModal)
        win.show()

        return win

    def __init__(self, parent: QWidget, filepath: str) -> None:
        super().__init__(parent)

        self.filepath_label: QLabel

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.filepath_label.setText(f'Loading data file: {filepath}')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self.setFixedSize(self.sizeHint())
