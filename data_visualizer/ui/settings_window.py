from PyQt6 import uic
from PyQt6.QtCore import QSettings, pyqtSlot
from PyQt6.QtWidgets import (QComboBox, QDoubleSpinBox, QMainWindow,
                             QPushButton, QSpinBox, QWidget)

_UI_FILEPATH = './assets/uis/settings_window.ui'
_DEFAULT_GRID_OPACITY = 0.5
_DEFAULT_VERTICAL_MARGIN = 15
_DEFAULT_GRAPH_THEME = 'light'

class SettingsWindow(QMainWindow):
    def __init__(self,
                 settings: QSettings,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.settings = settings

        self.reset_geometry: QPushButton
        self.graph_grid_opacity: QDoubleSpinBox
        self.graph_theme: QComboBox
        self.graph_vertical_margin: QSpinBox
        self.apply: QPushButton

        uic.load_ui.loadUi(_UI_FILEPATH, self)

        self.reset_geometry.clicked.connect(self._reset_geometry_cb)
        self.apply.clicked.connect(self._apply_cb)

        self._load_current_settings()

    def _load_current_settings(self) -> None:
        self.graph_grid_opacity.setValue(self.settings.value('graph_grid_opacity', _DEFAULT_GRID_OPACITY, float))
        self.graph_theme.setCurrentText(self.settings.value('graph_theme', _DEFAULT_GRAPH_THEME, str))
        self.graph_vertical_margin.setValue(self.settings.value('graph_vertical_margin', _DEFAULT_VERTICAL_MARGIN, int))

    @pyqtSlot()
    def _reset_geometry_cb(self) -> None:
        for key in self.settings.allKeys():
            if key.startswith(('state_', 'geometry_')):
                self.settings.setValue(key, None)

    @pyqtSlot()
    def _apply_cb(self) -> None:
        self.settings.setValue('graph_grid_opacity', self.graph_grid_opacity.value())
        self.settings.setValue('graph_theme', self.graph_theme.currentText())
        self.settings.setValue('graph_vertical_margin', self.graph_vertical_margin.value())
