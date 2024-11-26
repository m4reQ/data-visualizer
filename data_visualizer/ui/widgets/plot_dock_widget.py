import datetime
import random
import time
import typing as t

import numpy as np
import pandas as pd
import pyqtgraph  # type: ignore[import-untyped]
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPen
from PyQt6.QtWidgets import QDockWidget, QSizePolicy, QWidget


class PlotDockWidget(QDockWidget):
    ALLOWED_DOCK_AREAS = Qt.DockWidgetArea.LeftDockWidgetArea
    MIN_PLOT_COLOR = 128
    MAX_PLOT_COLOR = 255

    def __init__(self,
                 series: pd.Series,
                 x_axis: t.Iterable[float],
                 x_min: datetime.datetime | datetime.date,
                 x_max: datetime.datetime | datetime.date,
                 parent: QWidget | None = None) -> None:
        super().__init__(str(series.name), parent)

        self._plot_color = _get_random_qt_color(self.MIN_PLOT_COLOR, self.MAX_PLOT_COLOR)
        self._plot_widget = pyqtgraph.PlotWidget()

        # self._plot_widget.plotItem.vb.disableAutoRange()
        self._plot_widget.plotItem.setAxisItems({'bottom': pyqtgraph.DateAxisItem(orientation='bottom')})
        self._plot_widget.plotItem.showGrid(True, True, 1.0)
        self._plot_widget.plotItem.addLegend()

        self._serie = self._plot_widget.plotItem.plot(
                x_axis,
                series.astype(np.int64),
                pen=_create_pen_with_color(self._plot_color),
                name=series.name)

        self.setAllowedAreas(self.ALLOWED_DOCK_AREAS)
        self.setWidget(self._plot_widget)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setObjectName(f'PlotDockWidget_{series.name}')
        self.setTitleBarWidget(QWidget())

        self.set_data_range(x_min, x_max)

    def set_data_range(self, min: datetime.datetime | datetime.date, max: datetime.datetime | datetime.date) -> None:
        self._plot_widget.setXRange(
            _datetime_to_unix_timestamp(min),
            _datetime_to_unix_timestamp(max),
            padding=0.0)

    def set_y_min(self, value: float) -> None:
        self._plot_widget.setYRange(
            value,
            self._get_y_axis_range()[1],
            padding=0.0)

    def set_y_max(self, value: float) -> None:
        self._plot_widget.setYRange(
            self._get_y_axis_range()[0],
            value,
            padding=0.0)

    def _get_y_axis_range(self) -> tuple[float, float]:
        return self._plot_widget.plotItem.getAxis('left').range

def _get_random_qt_color(_min: int, _max: int) -> QColor:
    return QColor(
        int(random.uniform(_min, _max)),
        int(random.uniform(_min, _max)),
        int(random.uniform(_min, _max)))

def _create_pen_with_color(color: QColor) -> QPen:
    return pyqtgraph.mkPen(color=color)

def _datetime_to_unix_timestamp(value: datetime.datetime | datetime.date) -> float:
    return time.mktime(value.timetuple())
