import datetime
import random
import time
import typing as t

import pandas as pd
import pyqtgraph  # type: ignore[import-untyped]
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QBrush, QColor, QPen
from PyQt6.QtWidgets import QDockWidget, QSizePolicy, QWidget

from data_visualizer.models.pandas_model import PandasModel

_ALLOWED_DOCK_AREAS = Qt.DockWidgetArea.LeftDockWidgetArea
_MISSING_RANGE_PEN: QPen = pyqtgraph.mkPen(color=QColor(255, 0, 0, 255), style=Qt.PenStyle.DotLine)
_MISSING_RANGE_BRUSH: QBrush = QBrush(QColor(194, 194, 194, 128), Qt.BrushStyle.BDiagPattern)
_MIN_PEN_COLOR = 128
_MAX_PEN_COLOR = 255

class PlotDockWidget(QDockWidget):
    def __init__(self,
                 settings: QSettings,
                 model: PandasModel,
                 series_name: str,
                 x_axis_values: t.Iterable[t.SupportsInt],
                 x_min: datetime.datetime | datetime.date,
                 x_max: datetime.datetime | datetime.date,
                 parent: QWidget | None = None) -> None:
        super().__init__(series_name, parent)

        self.setAllowedAreas(_ALLOWED_DOCK_AREAS)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setObjectName(f'PlotDockWidget_{series_name}')
        self.setTitleBarWidget(QWidget())

        self._plot_widget = pyqtgraph.PlotWidget()
        self._plot_widget.plotItem.setAxisItems({'bottom': pyqtgraph.DateAxisItem(orientation='bottom')})
        self._plot_widget.plotItem.showGrid(True, True, settings.value('graph_grid_opacity', 0.5, float))
        self._plot_widget.plotItem.addLegend()

        theme = settings.value('graph_theme', 'light', str)
        if theme == 'light':
            self._plot_widget.setBackground('white')

        self.setWidget(self._plot_widget)

        series = model.dataframe[series_name]

        self._series = self._plot_widget.plotItem.plot(
                x_axis_values,
                model.dataframe[series_name],
                connect='finite',
                pen=_create_random_color_pen(theme == 'light'),
                name=series_name)

        for _, row in model.missing_ranges[series_name].iterrows():
            self._plot_item.addItem(
                pyqtgraph.LinearRegionItem(
                    values=(
                        _datetime_to_unix_timestamp(row.start),
                        _datetime_to_unix_timestamp(row.end)),
                    pen=_MISSING_RANGE_PEN,
                    brush=_MISSING_RANGE_BRUSH,
                    movable=False))

        margins = self._plot_widget.plotItem.getContentsMargins()
        self._plot_widget.plotItem.setContentsMargins(
            margins[0],
            margins[1],
            settings.value('graph_vertical_margin', 15, int),
            margins[3])

        self.set_x_range(x_min, x_max)
        self.set_y_min(series.min())
        self.set_y_max(series.max())

    def set_x_range(self,
                    x_min: datetime.datetime | datetime.date,
                    x_max: datetime.datetime | datetime.date,) -> None:
        self._plot_widget.setXRange(
            _datetime_to_unix_timestamp(x_min),
            _datetime_to_unix_timestamp(x_max),
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

    @property
    def _plot_item(self) -> pyqtgraph.PlotItem:
        return self._plot_widget.plotItem

    def _get_y_axis_range(self) -> tuple[float, float]:
        return self._plot_item.getAxis('left').range

# TODO Add RETURN key handling in import window

def _get_random_qt_color(_min: int, _max: int) -> QColor:
    return QColor(
        int(random.uniform(_min, _max)),
        int(random.uniform(_min, _max)),
        int(random.uniform(_min, _max)))

def _create_random_color_pen(use_dark_colors: bool) -> QPen:
    if use_dark_colors:
        color = _get_random_qt_color(0, 180)
    else:
        color = _get_random_qt_color(128, 255)

    return pyqtgraph.mkPen(
        color=color,
        style=Qt.PenStyle.SolidLine)

def _datetime_to_unix_timestamp(value: datetime.datetime | datetime.date) -> float:
    return time.mktime(value.timetuple())
