import traceback

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLabel, QMainWindow, QWidget

_UI_FILEPATH = './assets/uis/error_window.ui'
_HEADER_COLOR = QColor('#fa1807')
_TEXT_COLOR = QColor('#7d0000')

class ErrorWindow(QMainWindow):
    def __init__(self, parent: QWidget, exc: Exception) -> None:
        super().__init__(parent)

        self.error_header: QLabel
        self.error_text: QLabel

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self._set_label_color(self.error_header, _HEADER_COLOR)
        self._set_label_color(self.error_text, _TEXT_COLOR)

        self.error_text.setText(''.join(traceback.format_exception(exc)))

        self._resize_to_content()

    def _resize_to_content(self) -> None:
        layout = self.layout()
        assert layout is not None

        self.setFixedSize(layout.sizeHint())

    def _set_label_color(self, label: QLabel, color: QColor) -> None:
        palette = label.palette()
        palette.setColor(label.foregroundRole(), color)
        label.setPalette(palette)

