import os

import pandas as pd
from PyQt6 import uic
from PyQt6.QtCore import QSettings, pyqtSlot
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import (QFileDialog, QHeaderView, QLineEdit, QMainWindow,
                             QTableView, QTabWidget)

from data_visualizer.data_importer import ImporterSettings, ImporterType
from data_visualizer.models.pandas_model import PandasModel
from data_visualizer.ui.csv_import_window import CSVImportWindow
from data_visualizer.ui.error_window import ErrorWindow

_UI_FILEPATH = './assets/uis/main_window.ui'
_SETTINGS_STATE_NAME = '_state'
_SETTINGS_GEOMETRY_NAME = '_geometry'

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings('m4reQ', 'data_visualizer')
        self.cur_value_edit: QLineEdit
        self.opened_editors: QTabWidget
        self.action_open: QAction
        self.action_open_recent: QAction
        self.action_exit: QAction

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.action_exit.triggered.connect(self._exit_action_callback)
        self.action_open.triggered.connect(self._open_action_callback)

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

    def _import_data(self, settings: ImporterSettings) -> pd.DataFrame:
        data: pd.DataFrame
        match settings:
            case ImporterSettings(ImporterType.CSV, filepath, config):
                if config is None:
                    data = pd.read_csv(
                        filepath,
                        low_memory=False)
                else:
                    data = pd.read_csv(
                        filepath,
                        low_memory=False,
                        sep=config.separator,
                        names=[x[0] for x in config.column_settings],
                        dtype={k: v for k, v in config.column_settings})

        return data

    def _create_tableview_for_dataframe(self, df: pd.DataFrame) -> QTableView:
        data_tableview = QTableView()
        data_tableview.setModel(PandasModel(df))

        horizontal_header = data_tableview.horizontalHeader()
        assert horizontal_header is not None

        horizontal_header.setStretchLastSection(True)

        data_tableview.setHorizontalHeader(horizontal_header)

        return data_tableview

    @pyqtSlot(ImporterSettings)
    def _import_requested_cb(self, settings: ImporterSettings) -> None:
        try:
            data = self._import_data(settings)
        except Exception as exc:
            error_window = ErrorWindow(self, exc)
            error_window.show()

            return

        self.opened_editors.addTab(
            self._create_tableview_for_dataframe(data),
            os.path.basename(settings.filepath))

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
