import datetime
import io

import pandas as pd
import pyqtgraph  # type: ignore[import-untyped]
from dateutil import relativedelta
from PyQt6 import uic
from PyQt6.QtCore import QSettings, Qt, pyqtSlot
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import (QLabel, QMainWindow, QScrollArea, QToolButton,
                             QVBoxLayout, QWidget)

from data_visualizer.models.pandas_model import PandasModel
from data_visualizer.ui.widgets.calendar_dialog import CalendarDialog
from data_visualizer.ui.widgets.plot_dock_widget import PlotDockWidget
from data_visualizer.ui.widgets.series_config_widget import SeriesConfigWidget

# TODO Use single GraphicsLayoutWidget (possibly with ScrollArea) to display mutliple plots and gain some performance

_DATE_FORMAT = '%d.%m.%Y'
_UI_FILEPATH = './assets/uis/graph_ex_window.ui'
_SETTINGS_GEOMETRY_NAME = 'geometry_graph'
_SETTINGS_STATE_NAME = 'state_graph'

class GraphToolWindow(QMainWindow):
    def __init__(self, data: PandasModel, settings: QSettings, parent: QWidget) -> None:
        super().__init__(parent)

        df = data.dataframe

        self.settings = settings
        self.data = data
        self.min_date: datetime.date = df.index.min().date()
        self.max_date: datetime.date = df.index.max().date()
        self.start_date = self.min_date
        self.end_date = self.max_date
        self.series = dict[str, pyqtgraph.PlotDataItem]()
        self.plot_widgets = self._create_plot_widgets()

        self.period_label: QLabel
        self.period_end_button: QToolButton
        self.period_end_label: QLabel
        self.period_start_button: QToolButton
        self.period_start_label: QLabel
        self.y_axis_controls: QScrollArea

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self._restore_geometry()

        self.period_label.setText(_build_period_length_str(self.start_date, self.end_date))
        self.period_start_label.setText(_format_date(self.start_date))
        self.period_end_label.setText(_format_date(self.end_date))
        self.period_start_button.clicked.connect(self._start_date_changed_cb)
        self.period_end_button.clicked.connect(self._end_date_changed_cb)

        layout = QVBoxLayout()

        for column_name in df.columns:
            column = df[column_name]
            widget = SeriesConfigWidget(
                column_name,
                column.min(),
                column.max())
            widget.setContentsMargins(0, 0, 0, 0)
            widget.min_value_changed.connect(self._change_y_axis_min)
            widget.max_value_changed.connect(self._change_y_axis_max)
            widget.show_checked.connect(self._set_plot_visible)

            layout.addWidget(widget)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addStretch(1)

        self.y_axis_controls.setLayout(layout)

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.settings.setValue(_SETTINGS_GEOMETRY_NAME, self.saveGeometry())
        self.settings.setValue(_SETTINGS_STATE_NAME, self.saveState())

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
        geometry = self.settings.value(_SETTINGS_GEOMETRY_NAME)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self.settings.value(_SETTINGS_STATE_NAME)
        if state is not None:
            self.restoreState(state)

    def _reconfigure_plots(self) -> None:
        for plot_widget in self.plot_widgets.values():
            plot_widget.set_x_range(self.start_date, self.end_date)

    def _set_plot_visible(self, series_name: str, is_shown: bool) -> None:
        widget = self.plot_widgets[series_name]
        max_left_axis_width = max(
            x._plot_widget.plotItem.getAxis('left').width()
            for x in self.plot_widgets.values())

        for _widget in self.plot_widgets.values():
            _widget._plot_widget.plotItem.getAxis('left').setWidth(max_left_axis_width)

        if is_shown:
            widget.setVisible(True)
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, widget)
        else:
            self.removeDockWidget(widget)

    def _create_plot_widgets(self) -> dict[str, PlotDockWidget]:
        # precompute timestamps here to save plot creation time
        x_axis_values = self.data.dataframe.index.map(pd.Timestamp.timestamp)
        return {
            k: PlotDockWidget(
                self.settings,
                self.data,
                k,
                x_axis_values,
                self.start_date,
                self.end_date)
            for k in self.data.dataframe.columns}

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
    return date.strftime(_DATE_FORMAT)
