import dataclasses
import enum

from PyQt6.QtCore import QSize
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QLabel, QStatusBar, QWidget


@dataclasses.dataclass
class _IconDef:
    filepath: str
    is_animated: bool = False

class StatusBarStatus(enum.Enum):
    OK = enum.auto()
    PROCESSING = enum.auto()
    FAILURE = enum.auto()

Icon = QPixmap | QMovie

class StatusBar(QStatusBar):
    _STATUS_ICON_DEFS = {
        StatusBarStatus.OK: _IconDef('./assets/icons/status_ok_icon.png'),
        StatusBarStatus.FAILURE: _IconDef('./assets/icons/status_failure_icon.png'),
        StatusBarStatus.PROCESSING: _IconDef('./assets/icons/status_loading_icon.png', True)}

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        # TODO Implement status icons
        self._status_icons = dict[StatusBarStatus, Icon]() # self._load_status_icons(self._STATUS_ICON_DEFS, None)
        self._status_label = QLabel(self)
        self._msg_label = QLabel(self)

        # self.addWidget(self._status_label)
        self.addWidget(self._msg_label)

        self.set_status(StatusBarStatus.OK)

    def set_status(self, status: StatusBarStatus) -> None:
        return

        icon = self._status_icons[status]
        if isinstance(icon, QMovie):
            self._status_label.setMovie(icon)
            icon.start()
        else:
            self._status_label.setPixmap(icon)

    def set_message(self, msg: str, status: StatusBarStatus | None = None) -> None:
        self.clear_message()
        self._msg_label.setText(msg)

        if status is not None:
            self.set_status(status)

    def clear_message(self) -> None:
        self._msg_label.clear()
        self.set_status(StatusBarStatus.OK)

    def _load_status_icons(self, defs: dict[StatusBarStatus, _IconDef], target_size: QSize | None = None) -> dict[StatusBarStatus, Icon]:
        return {k: self._load_status_icon(v, target_size) for k, v in defs.items()}

    def _load_status_icon(self, definition: _IconDef, target_size: QSize | None = None) -> Icon:
        res: Icon

        if definition.is_animated:
            res = QMovie(definition.filepath)
        else:
            res = QPixmap(definition.filepath)

        if target_size is not None:
            return self._scale_icon(res, target_size)

        return res

    def _scale_icon(self, icon: Icon, target_size: QSize) -> Icon:
        if isinstance(icon, QPixmap):
            return icon.scaled(target_size)

        icon.setScaledSize(target_size)
        return icon
