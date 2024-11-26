import datetime
import io
import typing as t

import pandas as pd
import pyqtgraph  # type: ignore[import-untyped]
from dateutil import relativedelta
from PyQt6 import uic
from PyQt6.QtCore import QSettings, Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (QCalendarWidget, QLabel, QMainWindow, QTabWidget,
                             QWidget)

from data_visualizer.ui.widgets.plot_config_widget import PlotConfigWidget
from data_visualizer.ui.widgets.plot_dock_widget import PlotDockWidget


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

        self.from_calendar: QCalendarWidget
        self.to_calendar: QCalendarWidget
        self.period_length: QLabel
        self.plot_configs: QTabWidget

        self.data = data
        self.series = dict[str, pyqtgraph.PlotDataItem]()

        uic.load_ui.loadUi(self.UI_FILEPATH, self)

        date_min: datetime.date = self.data.index.min().date()
        date_max: datetime.date = self.data.index.max().date()

        self._restore_geometry()
        self._configure_period_length(date_min, date_max)
        self._configure_range_calendars(date_min, date_max)
        self._configure_plot_config_widgets(data)
        self._plot_widgets = self._configure_plot_widgets(data)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.settings.setValue(self._SETTINGS_GEOMETRY_NAME, self.saveGeometry())
        self.settings.setValue(self._SETTINGS_STATE_NAME, self.saveState())

        super().closeEvent(a0)

    @pyqtSlot()
    def _date_range_changed_cb(self) -> None:
        min_date = self.from_calendar.selectedDate().toPyDate()
        max_date = self.to_calendar.selectedDate().toPyDate()

        self.period_length.setText(_build_period_length_str(min_date, max_date))

        for plot_widget in self._plot_widgets.values():
            plot_widget.set_data_range(min_date, max_date)

    def _change_y_axis_min(self, series_name: str, value: float) -> None:
        self._plot_widgets[series_name].set_y_min(value)

    def _change_y_axis_max(self, series_name: str, value: float) -> None:
        self._plot_widgets[series_name].set_y_max(value)

    def _restore_geometry(self) -> None:
        geometry = self.settings.value(self._SETTINGS_GEOMETRY_NAME)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self.settings.value(self._SETTINGS_STATE_NAME)
        if state is not None:
            self.restoreState(state)

    def _configure_plot_widgets(self, data: pd.DataFrame) -> dict[str, PlotDockWidget]:
        x_axis = data.index.map(lambda x: x.timestamp())
        widgets = dict[str, PlotDockWidget]()

        for column_name in data.columns:
            column = data[column_name]
            widget = PlotDockWidget(
                column,
                x_axis,
                self.from_calendar.selectedDate().toPyDate(),
                self.to_calendar.selectedDate().toPyDate())

            widgets[column_name] = widget

        return widgets

    def _show_plot_widget(self, series_name: str, is_shown: bool) -> None:
        widget = self._plot_widgets[series_name]
        if is_shown:
            widget.setVisible(True)
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, widget)
        else:
            self.removeDockWidget(widget)

    def _configure_plot_config_widgets(self, data: pd.DataFrame) -> None:
        # kw argument with default to prevent capturing reference to name instead of the actual value
        # can be safely ignored as mypy doesn't know how to read lambas with default kw arguments anyway
        for column_name in data.columns:
            column = data[column_name]
            self.plot_configs.addTab(
                PlotConfigWidget(
                    column.min(),
                    column.max(),
                    lambda value, name=column_name: self._change_y_axis_min(name, value), # type: ignore[misc]
                    lambda value, name=column_name: self._change_y_axis_max(name, value), # type: ignore[misc]
                    lambda is_shown, name=column_name: self._show_plot_widget(name, is_shown)), # type: ignore[misc]
                column_name)

    def _configure_period_length(self, date_min: datetime.date, date_max: datetime.date) -> None:
        self.period_length.setText(_build_period_length_str(date_min, date_max))

    def _configure_range_calendars(self, date_min: datetime.date, date_max: datetime.date) -> None:
        self.from_calendar.setDateRange(date_min, date_max)
        self.from_calendar.setSelectedDate(date_min)
        self.from_calendar.selectionChanged.connect(self._date_range_changed_cb)

        self.to_calendar.setDateRange(date_min, date_max)
        self.to_calendar.setSelectedDate(date_max)
        self.to_calendar.selectionChanged.connect(self._date_range_changed_cb)

def _build_period_length_str(start: datetime.date, end: datetime.date) -> str:
    string_builder = io.StringIO()

    period = relativedelta.relativedelta(end, start)
    if period.years > 0:
        string_builder.write(f'{period.years} year{'s' if period.years > 1 else ''},')

    if period.months > 0:
        string_builder.write(f'{period.months} month{'s' if period.months > 1 else ''},')

    if period.days > 0:
        string_builder.write(f'{period.days} day{'s' if period.days > 1 else ''}')

    return string_builder.getvalue()
