import os

import pandas as pd
from PyQt6 import uic
from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import (QAbstractButton, QButtonGroup, QComboBox,
                             QFileDialog, QFrame, QLineEdit, QMainWindow,
                             QPushButton, QRadioButton, QTableView,
                             QToolButton, QWidget)

from data_visualizer.data_importer import (CSVImporterConfig, ImporterSettings,
                                           ImporterType)
from data_visualizer.models.column_settings_model import ColumnSettingsModel

_UI_FILEPATH = './assets/uis/import_csv.ui'
_MANUAL_SETTINGS_BUTTON_IDX = 1
_DEFAULT_CSV_SEPARATOR = ','
_PD_DATATYPES: list[tuple[str, type]] = sorted([
    ('Datetime', pd.Timestamp),
    ('Time Delta', pd.Timedelta),
    ('Period', pd.Period),
    ('Interval', pd.Interval),
    ('Integer', pd.Int64Dtype),
    ('Float', pd.Float64Dtype),
    ('Categorical', pd.CategoricalDtype),
    ('Sparse', pd.SparseDtype),
    ('String', pd.StringDtype),
    ('Boolean', pd.BooleanDtype),
    ('Arrow', pd.ArrowDtype)],
    key=lambda x: x[0])

class CSVImportWindow(QMainWindow):
    import_requested = pyqtSignal(ImporterSettings)

    def __init__(self, parent: QWidget, initial_filepath: str = '') -> None:
        super().__init__(parent)

        self.filepath_edit: QLineEdit
        self.browse_files: QToolButton
        self.settings_manual: QRadioButton
        self.settings_auto_detect: QRadioButton
        self.csv_settings_select_group: QButtonGroup
        self.csv_manual_settings_frame: QFrame
        self.column_separator: QLineEdit
        self.columns_settings: QTableView
        self.column_name: QLineEdit
        self.column_data_type: QComboBox
        self.add_column: QPushButton
        self.import_button: QPushButton

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.filepath_edit.setText(initial_filepath)
        self.browse_files.clicked.connect(self._browse_files_cb)
        self.csv_settings_select_group.buttonToggled.connect(self._import_button_toggled_cb)
        self.add_column.clicked.connect(self._add_column_cb)
        self.columns_settings.setModel(ColumnSettingsModel())
        self.import_button.clicked.connect(self._import_clicked_cb)

        self._select_default_import_type_button()
        self._configure_default_manual_settings()
        self._configure_column_datatype_combo_box()

    def _configure_column_datatype_combo_box(self) -> None:
        for name, pd_type in _PD_DATATYPES:
            self.column_data_type.addItem(name, pd_type)

        self.column_data_type.setCurrentIndex(0)

    def _select_default_import_type_button(self) -> None:
        self.csv_settings_select_group.buttons()[0].setChecked(True)

    def _configure_default_manual_settings(self) -> None:
        self.column_separator.setText(_DEFAULT_CSV_SEPARATOR)
        self._set_manual_settings_widgets_enabled(False)

    def _set_manual_settings_widgets_enabled(self, enabled: bool) -> None:
        self.column_separator.setEnabled(enabled)
        self.columns_settings.setEnabled(enabled)
        self.column_name.setEnabled(enabled)
        self.column_data_type.setEnabled(enabled)
        self.add_column.setEnabled(enabled)

    @pyqtSlot()
    def _import_clicked_cb(self) -> None:
        filepath = self.filepath_edit.text()

        config: CSVImporterConfig | None = None
        if self.csv_settings_select_group.checkedButton() == self.settings_manual:
            model = self.columns_settings.model()
            assert isinstance(model, ColumnSettingsModel)

            config = CSVImporterConfig(
                    True,
                    self.column_separator.text(),
                    model.get_data())

        self.import_requested.emit(
            ImporterSettings(
                ImporterType.CSV,
                filepath,
                config))

        self.close()

    @pyqtSlot()
    def _add_column_cb(self) -> None:
        model = self.columns_settings.model()
        assert isinstance(model, ColumnSettingsModel)

        name = self.column_name.text()
        if not name:
            return

        data_type = self.column_data_type.currentData()
        model.add_column(name, data_type)

        self.column_name.clear()

    @pyqtSlot()
    def _browse_files_cb(self) -> None:
        base_dir = os.path.dirname(self.filepath_edit.text())

        open_result = QFileDialog.getOpenFileName(
            self,
            'Import Data',
            base_dir,
            'All Files (*);;CSV (*.csv)')
        if open_result is None or len(open_result[0]) == 0:
            return

        self.filepath_edit.setText(open_result[0])

    @pyqtSlot(QAbstractButton, bool)
    def _import_button_toggled_cb(self, button: QAbstractButton, is_checked: bool) -> None:
        if self.csv_settings_select_group.buttons().index(button) != _MANUAL_SETTINGS_BUTTON_IDX:
            return

        self._set_manual_settings_widgets_enabled(is_checked)