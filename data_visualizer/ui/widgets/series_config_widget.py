from PyQt6 import uic
from PyQt6.QtCore import (QAbstractAnimation, QParallelAnimationGroup,
                          QPropertyAnimation, Qt, pyqtSignal, pyqtSlot)
from PyQt6.QtWidgets import (QCheckBox, QDoubleSpinBox, QLabel, QScrollArea,
                             QToolButton, QWidget)

ANIMATION_DURATION_MS = 100

class SeriesConfigWidget(QWidget):
    UI_FILEPATH = './assets/uis/series_config_widget.ui'

    min_value_changed = pyqtSignal(str, float)
    max_value_changed = pyqtSignal(str, float)
    show_checked = pyqtSignal(str, bool)

    def __init__(self,
                 series_name: str,
                 y_min: float,
                 y_max: float,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.series_name = series_name

        self.toggle_animation = QParallelAnimationGroup(self)

        self.expand_button: QToolButton
        self.name_label: QLabel
        self.show_checkbox: QCheckBox
        self.max_spinbox: QDoubleSpinBox
        self.min_spinbox: QDoubleSpinBox
        self.contents: QScrollArea

        uic.load_ui.loadUi(self.UI_FILEPATH, self)

        self.name_label.setText(series_name)

        self.max_spinbox.setRange(y_min, y_max)
        self.max_spinbox.setValue(y_max)
        self.max_spinbox.valueChanged.connect(self._max_changed_cb)
        self.min_spinbox.setRange(y_min, y_max)
        self.min_spinbox.setValue(y_min)
        self.min_spinbox.valueChanged.connect(self._min_changed_cb)

        self.show_checkbox.clicked.connect(self._show_checked_cb)

        self.contents.setMinimumHeight(0)
        self.contents.setMaximumHeight(0)

        self.expand_button.setCheckable(True)
        self.expand_button.pressed.connect(self._expand_cb)

        self.toggle_animation.addAnimation(QPropertyAnimation(self, b'minimumHeight'))
        self.toggle_animation.addAnimation(QPropertyAnimation(self, b'maximumHeight'))
        self.toggle_animation.addAnimation(QPropertyAnimation(self.contents, b'maximumHeight'))

        height = self.sizeHint().height()
        collapsed_height = height - self.contents.maximumHeight()
        contents_height = self.contents.layout().sizeHint().height() # type: ignore[union-attr]

        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            assert isinstance(animation, QPropertyAnimation)

            animation.setDuration(ANIMATION_DURATION_MS)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + contents_height)

        content_animation = self.toggle_animation.animationAt(self.toggle_animation.animationCount() - 1)
        assert isinstance(content_animation, QPropertyAnimation)

        content_animation.setDuration(ANIMATION_DURATION_MS)
        content_animation.setStartValue(0)
        content_animation.setEndValue(contents_height)

    @pyqtSlot()
    def _expand_cb(self) -> None:
        is_checked = self.expand_button.isChecked()

        self.expand_button.setArrowType(Qt.ArrowType.RightArrow if is_checked else Qt.ArrowType.DownArrow)
        self.toggle_animation.setDirection(QAbstractAnimation.Direction.Backward if is_checked else QAbstractAnimation.Direction.Forward)
        self.toggle_animation.start()

    @pyqtSlot(float)
    def _max_changed_cb(self, value: float) -> None:
        self.max_value_changed.emit(self.series_name, value)

    @pyqtSlot(float)
    def _min_changed_cb(self, value: float) -> None:
        self.min_value_changed.emit(self.series_name, value)

    @pyqtSlot()
    def _show_checked_cb(self) -> None:
        self.show_checked.emit(self.series_name, self.show_checkbox.isChecked())
