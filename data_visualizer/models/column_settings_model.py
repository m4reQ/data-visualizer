import typing as t

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt


class ColumnSettingsModel(QAbstractTableModel):
    _HEADERS = ('name', 'type')

    def __init__(self):
        super().__init__()

        self._data = list[tuple[str, type]]()

    def add_column(self, name: str, data_type: type) -> None:
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._data.append((name, data_type))
        self.endInsertRows()

    def get_data(self) -> list[tuple[str, type]]:
        return self._data

    def data(self, index: QModelIndex, role: int = 0) -> t.Any:
        if role == Qt.ItemDataRole.DisplayRole:
            data = self._data[index.row()][index.column()]
            if index.column() == 1:
                assert isinstance(data, type)
                return data.__name__

            return data

    def rowCount(self, _: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, _: QModelIndex = QModelIndex()) -> int:
        return 2

    def headerData(self,
                   section: int,
                   orientation: Qt.Orientation,
                   role: int = 0) -> t.Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._HEADERS[section]

            if orientation == Qt.Orientation.Vertical:
                return str(section)
