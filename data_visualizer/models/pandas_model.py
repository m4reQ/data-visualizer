from typing import Any

import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt


class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__()

        self._data = df

    def data(self, index: QModelIndex, role: int = 0) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            data = self._data.iat[index.row(), index.column()]
            return str(data)

    def rowCount(self, _: QModelIndex = QModelIndex()) -> int:
        return self._data.shape[0]

    def columnCount(self, _: QModelIndex = QModelIndex()) -> int:
        return self._data.shape[1]

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = 0) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data.columns[section]

            if orientation == Qt.Orientation.Vertical:
                return str(section)
