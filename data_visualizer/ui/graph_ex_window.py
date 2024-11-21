import datetime
import io
import random
import time
import typing as t

import numpy as np
import pandas as pd
import pyqtgraph  # type: ignore[import-untyped]
from dateutil import relativedelta
from PyQt6 import uic
from PyQt6.QtCore import QSettings, Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent, QColor, QPen
from PyQt6.QtWidgets import (QCalendarWidget, QLabel, QMainWindow, QSpinBox,
                             QWidget)

_MIN_COLOR = 128
_MAX_COLOR = 255

class GraphExToolWindow(QMainWindow):
    UI_FILEPATH = './assets/uis/graph_ex_window.ui'
    _SETTINGS_GEOMETRY_NAME = 'graph_geometry'
    _SETTINGS_STATE_NAME = 'graph_state'

    @classmethod
    def open_blocking(cls, parent: QWidget, settings: QSettings, data: pd.DataFrame) -> t.Self:
        win = cls(parent, settings, data)
        win.setWindowModality(Qt.WindowModality.ApplicationModal)
        win.show()

        return win

    @classmethod
    def open(cls, parent: QWidget, settings: QSettings, data: pd.DataFrame) -> t.Self:
        win = cls(parent, settings, data)
        win.show()

        return win

    def __init__(self, parent: QWidget, settings: QSettings, data: pd.DataFrame) -> None:
        super().__init__(parent)

        self.settings = settings

        self.graph_widget: pyqtgraph.PlotWidget
        self.y_axis_min: QSpinBox
        self.y_axis_max: QSpinBox
        self.from_calendar: QCalendarWidget
        self.to_calendar: QCalendarWidget
        self.period_length: QLabel

        self.data = data
        self.series = dict[str, pyqtgraph.PlotDataItem]()

        uic.load_ui.loadUi(self.UI_FILEPATH, self)

        self._restore_geometry()
        self._configure()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.settings.setValue(self._SETTINGS_GEOMETRY_NAME, self.saveGeometry())
        self.settings.setValue(self._SETTINGS_STATE_NAME, self.saveState())

        super().closeEvent(a0)

    @pyqtSlot()
    def _date_range_changed_cb(self) -> None:
        from_date = self.from_calendar.selectedDate().toPyDate()
        to_date = self.to_calendar.selectedDate().toPyDate()

        self.period_length.setText(_build_period_length_str(from_date, to_date))

        from_ts = _datetime_to_unix_timestamp(from_date)
        to_ts = _datetime_to_unix_timestamp(to_date)

        self.graph_widget.setXRange(from_ts, to_ts)

    @pyqtSlot(int)
    def _y_axis_min_changed(self, value: int) -> None:
        y_axis: pyqtgraph.AxisItem = self.graph_widget.plotItem.getAxis('left')
        # FIXME Retrieve another end of the range, as it is required for this function
        self.graph_widget.setYRange(value, y_axis.range[1])

    @pyqtSlot(int)
    def _y_axis_max_changed(self, value: int) -> None:
        y_axis: pyqtgraph.AxisItem = self.graph_widget.plotItem.getAxis('left')

        self.graph_widget.setYRange(y_axis.range[0], value)

    def _restore_geometry(self) -> None:
        geometry = self.settings.value(self._SETTINGS_GEOMETRY_NAME)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self.settings.value(self._SETTINGS_STATE_NAME)
        if state is not None:
            self.restoreState(state)

    def _configure(self) -> None:
        dt_min: datetime.date = self.data.index.min().date()
        dt_max: datetime.date = self.data.index.max().date()

        self.period_length.setText(_build_period_length_str(dt_min, dt_max))

        self.from_calendar.setDateRange(dt_min, dt_max)
        self.from_calendar.setSelectedDate(dt_min)
        self.from_calendar.selectionChanged.connect(self._date_range_changed_cb)

        self.to_calendar.setDateRange(dt_min, dt_max)
        self.to_calendar.setSelectedDate(dt_max)
        self.to_calendar.selectionChanged.connect(self._date_range_changed_cb)

        y_min = int(self.data.min().min())
        y_max = int(self.data.max().max())

        self.y_axis_min.setValue(y_min)
        self.y_axis_min.valueChanged.connect(self._y_axis_min_changed)

        self.y_axis_max.setValue(y_max)
        self.y_axis_max.valueChanged.connect(self._y_axis_max_changed)

        plot_item = self.graph_widget.plotItem
        assert isinstance(plot_item, pyqtgraph.PlotItem)

        plot_item.setAxisItems({'bottom': pyqtgraph.DateAxisItem(orientation='bottom')})
        plot_item.addLegend()

        x_axis = self.data.index.map(lambda x: x.timestamp()).to_list()

        for i, (name, column) in enumerate(self.data.items()):
            assert isinstance(name, str)

            if i == 0:
                continue

            color = _get_random_qt_color(_MIN_COLOR, _MAX_COLOR)

            serie = plot_item.plot(
                x_axis,
                column.astype(np.int64).to_list(),
                pen=_create_pen_with_color(color),
                name=name)

            self.series[name] = serie

def _get_random_qt_color(_min: int, _max: int) -> QColor:
    return QColor(
        int(random.uniform(_min, _max)),
        int(random.uniform(_min, _max)),
        int(random.uniform(_min, _max)))

def _create_pen_with_color(color: QColor) -> QPen:
    return pyqtgraph.mkPen(color=color)

def _datetime_to_unix_timestamp(value: datetime.datetime | datetime.date) -> float:
    return time.mktime(value.timetuple())

def _build_period_length_str(start: datetime.date, end: datetime.date) -> str:
    string_builder = io.StringIO()

    period = relativedelta.relativedelta(end, start)
    if period.years > 0:
        string_builder.write(f'{period.years} year(s), ')

    if period.months > 0:
        string_builder.write(f'{period.months} month(s), ')

    if period.days > 0:
        string_builder.write(f'{period.days} day(s)')

    return string_builder.getvalue()
