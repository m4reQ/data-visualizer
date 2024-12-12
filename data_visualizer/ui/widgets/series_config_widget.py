import typing as t

from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QCheckBox, QDoubleSpinBox, QFrame, QLabel,
                             QScrollArea, QToolButton, QWidget)

_SeriesConfigWidgetClass: t.TypeAlias = uic.load_ui.loadUiType('./assets/uis/series_config_widget.ui')[0] # type: ignore

class SeriesConfigWidget(QWidget, _SeriesConfigWidgetClass):
    min_value_changed = pyqtSignal(str, float)
    max_value_changed = pyqtSignal(str, float)
    show_checked = pyqtSignal(str, bool)

    def __init__(self,
                 series_name: str,
                 y_min: float,
                 y_max: float,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setupUi(self)

        self.series_name = series_name

        self.expand_button: QToolButton
        self.name_label: QLabel
        self.show_checkbox: QCheckBox
        self.max_spinbox: QDoubleSpinBox
        self.min_spinbox: QDoubleSpinBox
        self.contents: QFrame

        self.name_label.setText(series_name)

        self.max_spinbox.setRange(y_min, y_max)
        self.max_spinbox.setValue(y_max)
        self.max_spinbox.valueChanged.connect(self._max_changed_cb)
        self.min_spinbox.setRange(y_min, y_max)
        self.min_spinbox.setValue(y_min)
        self.min_spinbox.valueChanged.connect(self._min_changed_cb)

        self.show_checkbox.clicked.connect(self._show_checked_cb)

        self.contents_height = self.contents.layout().sizeHint().height() # type: ignore[union-attr]
        self.expanded_height = self.sizeHint().height()
        self.collapsed_height = self.expanded_height - self.contents_height

        self.contents.setFixedHeight(0)
        self.setFixedHeight(self.collapsed_height)

        self.expand_button.setCheckable(True)
        self.expand_button.clicked.connect(self._expand_cb)

    @pyqtSlot()
    def _expand_cb(self) -> None:
        is_checked = self.expand_button.isChecked()

        self.expand_button.setArrowType(Qt.ArrowType.DownArrow if is_checked else Qt.ArrowType.RightArrow)

        if is_checked:
            self.contents.setFixedHeight(self.contents_height)
            self.setFixedHeight(self.collapsed_height + self.contents_height)
        else:
            self.contents.setFixedHeight(0)
            self.setFixedHeight(self.collapsed_height)

    @pyqtSlot(float)
    def _max_changed_cb(self, value: float) -> None:
        self.max_value_changed.emit(self.series_name, value)

    @pyqtSlot(float)
    def _min_changed_cb(self, value: float) -> None:
        self.min_value_changed.emit(self.series_name, value)

    @pyqtSlot()
    def _show_checked_cb(self) -> None:
        self.show_checked.emit(self.series_name, self.show_checkbox.isChecked())
