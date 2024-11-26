import os

import pandas as pd
from PyQt6 import uic
from PyQt6.QtCore import QSettings, QThreadPool, pyqtSlot
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import (QFileDialog, QLineEdit, QMainWindow, QTableView,
                             QTabWidget)

from data_visualizer.data_importer import ImporterSettings, ImporterType
from data_visualizer.models.pandas_model import PandasModel
from data_visualizer.qt_job import Job
from data_visualizer.ui.csv_import_window import CSVImportWindow
from data_visualizer.ui.error_window import ErrorWindow
from data_visualizer.ui.graph_ex_window import GraphExToolWindow
from data_visualizer.ui.loading_window import LoadingWindow
from data_visualizer.ui.status_bar import StatusBar, StatusBarStatus

_UI_FILEPATH = './assets/uis/main_window.ui'
_SETTINGS_STATE_NAME = '_state'
_SETTINGS_GEOMETRY_NAME = '_geometry'

# TODO SEPARATION OF CONCERNS!!! (move logic from the ui)

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings('m4reQ', 'data_visualizer')
        self.thread_pool = QThreadPool(self)
        self.loading_window: LoadingWindow | None = None

        self.cur_value_edit: QLineEdit
        self.opened_editors: QTabWidget
        self.status_bar: StatusBar

        # actions
        self.action_open: QAction
        self.action_open_recent: QAction
        self.action_exit: QAction
        self.action_generate_graph: QAction
        self.action_generate_histogram: QAction

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.action_exit.triggered.connect(self._exit_action_callback)
        self.action_open.triggered.connect(self._open_action_callback)
        self.action_generate_graph.triggered.connect(self._open_graph_window)

        self._restore_geometry()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self.settings.setValue(_SETTINGS_GEOMETRY_NAME, self.saveGeometry())
        self.settings.setValue(_SETTINGS_STATE_NAME, self.saveState())

        super().closeEvent(a0)

    def _restore_geometry(self) -> None:
        geometry = self.settings.value(_SETTINGS_GEOMETRY_NAME)
        if geometry is not None:
            self.restoreGeometry(geometry)

        state = self.settings.value(_SETTINGS_STATE_NAME)
        if state is not None:
            self.restoreState(state)

    def _import_data(self, settings: ImporterSettings) -> tuple[pd.DataFrame, str]:
        data: pd.DataFrame
        match settings:
            case ImporterSettings(ImporterType.CSV, filepath, config):
                dtype = None
                names = None
                if config.column_settings is not None:
                    dtype = {k: v for k, v in config.column_settings}
                    names = [x[0] for x in config.column_settings]

                data = pd.read_csv(
                    filepath,
                    low_memory=False,
                    parse_dates=True,
                    index_col=config.index_column,
                    sep=config.separator,
                    names=names,
                    dtype=dtype,
                    date_format=config.datetime_format)

        # TODO Unhardcode this
        data.index = pd.to_datetime(data.index, utc=True)

        return (data, settings.filepath)

    def _create_tableview_for_dataframe(self, df: pd.DataFrame) -> QTableView:
        data_tableview = QTableView()
        data_tableview.setModel(PandasModel(df))

        horizontal_header = data_tableview.horizontalHeader()
        assert horizontal_header is not None

        horizontal_header.setStretchLastSection(True)

        data_tableview.setHorizontalHeader(horizontal_header)

        return data_tableview

    def _get_current_data_model(self) -> PandasModel:
        current_tab = self.opened_editors.currentWidget()
        assert isinstance(current_tab, QTableView)

        model = current_tab.model()
        assert isinstance(model, PandasModel)

        return model

    @pyqtSlot()
    def _open_graph_window(self) -> None:
        GraphExToolWindow.open_blocking(
            self,
            self.settings,
            self._get_current_data_model().get_data())

    @pyqtSlot(Exception)
    def _exception_cb(self, exc: Exception) -> None:
        ErrorWindow.open_blocking(self, exc)

    @pyqtSlot(pd.DataFrame)
    def _loading_finished_cb(self, data: tuple[pd.DataFrame, str]) -> None:
        self.opened_editors.addTab(
            self._create_tableview_for_dataframe(data[0]),
            os.path.basename(data[1]))

        if self.loading_window is not None:
            self.loading_window.close()

        self.status_bar.clear_message()

    @pyqtSlot(ImporterSettings)
    def _import_requested_cb(self, settings: ImporterSettings) -> None:
        job = Job(self._import_data, settings)
        job.error.connect(self._exception_cb)
        job.finished.connect(self._loading_finished_cb)

        self.thread_pool.start(job)

        self.status_bar.set_message(
            f'Importing data from "{settings.filepath}"...',
            StatusBarStatus.PROCESSING)

    @pyqtSlot()
    def _open_action_callback(self) -> None:
        open_result = QFileDialog.getOpenFileName(
            self,
            'Import data',
            '.',
            'All Files (*);;CSV files (*.csv)')
        if open_result is None or len(open_result[0]) == 0:
            return

        import_window = CSVImportWindow(self, open_result[0])
        import_window.import_requested.connect(self._import_requested_cb)
        import_window.show()

    @pyqtSlot()
    def _exit_action_callback(self) -> None:
        self.close()
