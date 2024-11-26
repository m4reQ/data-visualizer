import typing as t

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDoubleSpinBox, QPushButton, QWidget


class PlotConfigWidget(QWidget):
    UI_FILEPATH = './assets/uis/plot_config.ui'

    def __init__(self,
                 y_min: float,
                 y_max: float,
                 on_min_value_changed: t.Callable[[float], t.Any],
                 on_max_value_changed: t.Callable[[float], t.Any],
                 on_show_clicked: t.Callable[[bool], t.Any],
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.is_shown = False

        self.y_axis_min: QDoubleSpinBox
        self.y_axis_max: QDoubleSpinBox
        self.show_button: QPushButton

        self.on_show_clicked = on_show_clicked

        uic.load_ui.loadUi(self.UI_FILEPATH, self)

        self.y_axis_min.setValue(y_min)
        self.y_axis_min.valueChanged.connect(pyqtSlot(float)(on_min_value_changed))

        self.y_axis_max.setValue(y_max)
        self.y_axis_max.valueChanged.connect(pyqtSlot(float)(on_max_value_changed))

        self.show_button.clicked.connect(self._show_clicked_cb)

    @pyqtSlot()
    def _show_clicked_cb(self) -> None:
        self.is_shown = not self.is_shown

        self.show_button.setText('Hide' if self.is_shown else 'Show')

        self.on_show_clicked(self.is_shown)
