import datetime
import os

import numpy as np
import pandas as pd
from PyQt6 import uic
from PyQt6.QtCore import (QItemSelection, QModelIndex, QSettings, Qt,
                          QThreadPool, pyqtSlot)
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import (QFileDialog, QLabel, QLineEdit, QMainWindow,
                             QTableView, QTabWidget)

from data_visualizer.data_importer import ImporterSettings, ImporterType
from data_visualizer.models.pandas_model import PandasModel
from data_visualizer.qt_job import Job
from data_visualizer.ui.csv_import_window import CSVImportWindow
from data_visualizer.ui.error_window import ErrorWindow
from data_visualizer.ui.graph_window import GraphToolWindow
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

        self.cur_value_edit: QLineEdit
        self.opened_editors: QTabWidget
        self.status_bar: StatusBar

        # info
        self.size_unit: QLabel
        self.size_label: QLabel
        self.current_col_name: QLabel
        self.current_columns: QLabel
        self.current_rows: QLabel
        self.current_filepath: QLabel
        self.current_last_edited: QLabel

        # actions
        self.action_open: QAction
        self.action_open_recent: QAction
        self.action_exit: QAction
        self.action_generate_graph: QAction

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.action_exit.triggered.connect(self._exit_action_callback)
        self.action_open.triggered.connect(self._open_action_callback)
        self.action_generate_graph.triggered.connect(self._open_graph_window)
        self.opened_editors.currentChanged.connect(self._editor_selection_changed)

        self._restore_geometry()

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        self._save_geometry()
        super().closeEvent(a0)

    def _save_geometry(self) -> None:
        self.settings.setValue(_SETTINGS_GEOMETRY_NAME, self.saveGeometry())
        self.settings.setValue(_SETTINGS_STATE_NAME, self.saveState())

    def _restore_geometry(self) -> None:
        if (geometry := self.settings.value(_SETTINGS_GEOMETRY_NAME)) is not None:
            self.restoreGeometry(geometry)

        if (state := self.settings.value(_SETTINGS_STATE_NAME)) is not None:
            self.restoreState(state)

    def _import_data(self, settings: ImporterSettings) -> PandasModel:
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

        dummy = pd.DataFrame(
            np.nan,
            index=pd.date_range(
                data.index.min(),
                data.index.max(),
                freq='min'),
            columns=data.columns)
        dummy.index.name = data.index.name
        result = dummy.combine_first(data)

        return PandasModel(result, filepath)

    def _get_current_data_model(self) -> PandasModel:
        current_tab = self.opened_editors.currentWidget()
        assert isinstance(current_tab, QTableView)

        model = current_tab.model()
        assert isinstance(model, PandasModel)

        return model

    @pyqtSlot(int)
    def _editor_selection_changed(self, index: int) -> None:
        if index == -1:
            return

        model = self._get_current_data_model()
        self._update_info_tab(model)

        selection: QItemSelection = self.opened_editors.currentWidget().selectionModel().selection() # type: ignore[union-attr]
        if selection.count() == 0:
            return

        self._update_current_value_display(
            model,
            selection.indexes()[0])

    @pyqtSlot()
    def _open_graph_window(self) -> None:
        GraphToolWindow.open_blocking(
            self,
            self.settings,
            self._get_current_data_model())

    @pyqtSlot(Exception)
    def _exception_cb(self, exc: Exception) -> None:
        ErrorWindow.open_blocking(self, exc)

    @pyqtSlot(pd.DataFrame)
    def _loading_finished_cb(self, data: PandasModel) -> None:
        self.opened_editors.addTab(
            self._create_tableview_for_model(data),
            os.path.basename(data.filepath))

        self.action_generate_graph.setEnabled(True)
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

    @pyqtSlot(QItemSelection, QItemSelection)
    def _table_selection_changed(self, selected: QItemSelection, _) -> None:
        if selected.count() == 0:
            return

        self._update_current_value_display(
            self._get_current_data_model(),
            selected.first().indexes()[0])

    def _update_current_value_display(self, model: PandasModel, index: QModelIndex) -> None:
        self.cur_value_edit.setText(str(model.data(index)))

        column_name = model.headerData(index.column(), Qt.Orientation.Horizontal) # type: ignore[assignment]
        self.current_col_name.setText(column_name)

    def _update_info_tab(self, model: PandasModel) -> None:
        dataframe = model.dataframe
        filepath = model.filepath

        self.size_label.setText(f'{(dataframe.memory_usage(index=True).sum() / 1_000):.2f}')
        self.size_unit.setText('kB')
        self.current_rows.setText(f'{dataframe.shape[0]}')
        self.current_columns.setText(f'{dataframe.shape[1]}')
        self.current_filepath.setText(filepath)

        last_modified_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        self.current_last_edited.setText(last_modified_time.strftime('%d/%m/%Y, %H:%M:%S'))

    def _create_tableview_for_model(self, model: PandasModel) -> QTableView:
        data_tableview = QTableView()
        data_tableview.setModel(model)
        data_tableview.horizontalHeader().setStretchLastSection(True) # type: ignore[union-attr]
        data_tableview.selectionModel().selectionChanged.connect(self._table_selection_changed) # type: ignore[union-attr]

        return data_tableview

