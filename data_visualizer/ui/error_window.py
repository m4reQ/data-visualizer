import traceback
import typing as t

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QMainWindow, QWidget

ErrorWindowClass: t.TypeAlias = uic.load_ui.loadUiType('./assets/uis/error_window.ui')[0] # type: ignore

class ErrorWindow(QMainWindow, ErrorWindowClass):
    @classmethod
    def open_blocking(cls, parent: QWidget, exc: Exception) -> t.Self:
        win = cls(parent, exc)
        win.setWindowModality(Qt.WindowModality.ApplicationModal)
        win.show()

        return win

    def __init__(self, parent: QWidget, exc: Exception) -> None:
        super().__init__(parent)

        self.setupUi(self)

        self.error_header: QLabel
        self.error_text: QLabel

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.error_text.setText(''.join(traceback.format_exception(exc)))

        self._resize_to_content()

    def _resize_to_content(self) -> None:
        layout = self.layout()
        assert layout is not None

        self.setFixedSize(layout.sizeHint())

