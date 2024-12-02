import datetime
import io
import typing as t

import pandas as pd
import pyqtgraph  # type: ignore[import-untyped]
from dateutil import relativedelta
from PyQt6 import uic
from PyQt6.QtCore import QSettings, Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (QLabel, QMainWindow, QScrollArea, QToolButton,
                             QVBoxLayout, QWidget)

from data_visualizer.ui.widgets.calendar_dialog import CalendarDialog
from data_visualizer.ui.widgets.plot_dock_widget import PlotDockWidget
from data_visualizer.ui.widgets.series_config_widget import SeriesConfigWidget

# TODO Use single GraphicsLayoutWidget (possibly with ScrollArea) to display mutliple plots and gain some performance

DATE_FORMAT = '%d.%m.%Y'

class GraphToolWindow(QMainWindow):
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
        self.data = data
        self.min_date: datetime.date = self.data.index.min().date()
        self.max_date: datetime.date = self.data.index.max().date()
        self.start_date = self.min_date
        self.end_date = self.max_date
        self.series = dict[str, pyqtgraph.PlotDataItem]()
        self.plot_widgets = _create_plot_widgets(data, self.start_date, self.end_date)

        self.period_label: QLabel
        self.period_end_button: QToolButton
        self.period_end_label: QLabel
        self.period_start_button: QToolButton
        self.period_start_label: QLabel
        self.y_axis_controls: QScrollArea

        uic.load_ui.loadUi(self.UI_FILEPATH, self)

        self._restore_geometry()

        self.period_label.setText(_build_period_length_str(self.start_date, self.end_date))
        self.period_start_label.setText(_format_date(self.start_date))
        self.period_end_label.setText(_format_date(self.end_date))
        self.period_start_button.clicked.connect(self._start_date_changed_cb)
        self.period_end_button.clicked.connect(self._end_date_changed_cb)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        for column_name in data.columns:
            column = data[column_name]
            widget = SeriesConfigWidget(
                column_name,
                column.min(),
                column.max())
            widget.min_value_changed.connect(self._change_y_axis_min)
            widget.max_value_changed.connect(self._change_y_axis_max)
            widget.show_checked.connect(self._set_plot_visible)

            layout.addWidget(widget)

        layout.addStretch()

        self.y_axis_controls.setLayout(layout)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.settings.setValue(self._SETTINGS_GEOMETRY_NAME, self.saveGeometry())
        self.settings.setValue(self._SETTINGS_STATE_NAME, self.saveState())

        super().closeEvent(a0)

    @pyqtSlot()
    def _start_date_changed_cb(self) -> None:
        self.start_date = CalendarDialog.get_date(
            'Select start date',
            self.min_date,
            self.max_date,
            self.start_date,
            self)

        self.period_start_label.setText(_format_date(self.start_date))
        self.period_label.setText(_build_period_length_str(self.start_date, self.end_date))

        self._reconfigure_plots()

    @pyqtSlot()
    def _end_date_changed_cb(self) -> None:
        self.end_date = CalendarDialog.get_date(
            'Select end date',
            self.min_date,
            self.max_date,
            self.end_date,
            self)

        self.period_end_label.setText(_format_date(self.end_date))
        self.period_label.setText(_build_period_length_str(self.start_date, self.end_date))

        self._reconfigure_plots()

    def _change_y_axis_min(self, series_name: str, value: float) -> None:
        self.plot_widgets[series_name].set_y_min(value)

    def _change_y_axis_max(self, series_name: str, value: float) -> None:
        self.plot_widgets[series_name].set_y_max(value)

    def _restore_geometry(self) -> None:
        geometry = self.settings.value(self._SETTINGS_GEOMETRY_NAME)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self.settings.value(self._SETTINGS_STATE_NAME)
        if state is not None:
            self.restoreState(state)

    def _reconfigure_plots(self) -> None:
        for plot_widget in self.plot_widgets.values():
            plot_widget.set_data_range(self.start_date, self.end_date)

    def _set_plot_visible(self, series_name: str, is_shown: bool) -> None:
        widget = self.plot_widgets[series_name]

        if is_shown:
            widget.setVisible(True)
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, widget)
        else:
            self.removeDockWidget(widget)

def _build_period_length_str(start: datetime.date, end: datetime.date) -> str:
    string_builder = io.StringIO()

    period = relativedelta.relativedelta(end, start)
    if period.years > 0:
        string_builder.write(f'{period.years} year{'s' if period.years > 1 else ''}')

    if period.months > 0:
        if period.years > 0:
            string_builder.write(', ')

        string_builder.write(f'{period.months} month{'s' if period.months > 1 else ''},')

    if period.days > 0:
        if period.years > 0 or period.months > 0:
            string_builder.write(', ')

        string_builder.write(f'{period.days} day{'s' if period.days > 1 else ''}')

    return string_builder.getvalue()

def _format_date(date: datetime.date) -> str:
    return date.strftime(DATE_FORMAT)

def _create_plot_widgets(data: pd.DataFrame,
                         start_date: datetime.date,
                         end_date: datetime.date) -> dict[str, PlotDockWidget]:
    x_axis_values = data.index.map(lambda x: x.timestamp())

    return {
        k: PlotDockWidget(data[k], x_axis_values, start_date, end_date)
        for k in data.columns}
