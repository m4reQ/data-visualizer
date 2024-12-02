from PyQt6.QtCore import (QAbstractAnimation, QParallelAnimationGroup,
                          QPropertyAnimation, Qt, pyqtSlot)
from PyQt6.QtWidgets import (QFrame, QLayout, QScrollArea, QSizePolicy,
                             QToolButton, QWidget)

ANIMATION_DURATION_MS = 500

class ExpandableWidget(QWidget):
    def __init__(self,
                 title: str = '',
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._content_area = QScrollArea(self)
        self._toggle_animation = QParallelAnimationGroup(self)
        self._toggle_button = QToolButton(self)

        self._content_area.setMinimumHeight(0)
        self._content_area.setMaximumHeight(0)

        self._toggle_button.setText(title)
        self._toggle_button.setCheckable(True)
        self._toggle_button.setChecked(False)

        self._toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle_button.setArrowType(Qt.ArrowType.RightArrow)
        self._toggle_button.pressed.connect(self._pressed_callback)

        self._content_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._content_area.setFrameShape(QFrame.Shape.NoFrame)

        self._toggle_animation.addAnimation(QPropertyAnimation(self, b'minimumHeight'))
        self._toggle_animation.addAnimation(QPropertyAnimation(self, b'maximumHeight'))
        self._toggle_animation.addAnimation(QPropertyAnimation(self._content_area, b'maximumHeight'))

    def set_content_layout(self, layout: QLayout) -> None:
        self._content_area.setLayout(layout)

        height = self.sizeHint().height()
        collapsed_height = height - self._content_area.maximumHeight()
        content_height = layout.sizeHint().height()

        for i in range(self._toggle_animation.animationCount()):
            animation = self._toggle_animation.animationAt(i)
            assert isinstance(animation, QPropertyAnimation)

            animation.setDuration(ANIMATION_DURATION_MS)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self._toggle_animation.animationAt(self._toggle_animation.animationCount() - 1)
        assert isinstance(content_animation, QPropertyAnimation)

        content_animation.setDuration(ANIMATION_DURATION_MS)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)

    @pyqtSlot()
    def _pressed_callback(self) -> None:
        is_checked = self._toggle_button.isChecked()

        self._toggle_button.setArrowType(Qt.ArrowType.DownArrow if is_checked else Qt.ArrowType.RightArrow)
        self._toggle_animation.setDirection(QAbstractAnimation.Direction.Backward if is_checked else QAbstractAnimation.Direction.Forward)
        self._toggle_animation.start()
