import dataclasses
import datetime
import itertools
from typing import Any

import pandas as pd
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt


@dataclasses.dataclass
class MissingRange:
    start: datetime.datetime
    end: datetime.datetime
    length: int

class PandasModel(QAbstractTableModel):
    def __init__(self, df: pd.DataFrame, filepath: str) -> None:
        super().__init__()

        self.dataframe = df
        self.missing_ranges = _get_missing_ranges(df)
        self.filepath = filepath

    def data(self, index: QModelIndex, role: int = 0) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return str(self.dataframe.index[index.row()])

            return str(self.dataframe.iat[index.row(), index.column() - 1])

    def rowCount(self, _: QModelIndex = QModelIndex()) -> int:
        return self.dataframe.shape[0]

    def columnCount(self, _: QModelIndex = QModelIndex()) -> int:
        return self.dataframe.shape[1] + 1

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = 0) -> str:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                if section == 0:
                    return self.dataframe.index.name

                return self.dataframe.columns[section - 1]

            if orientation == Qt.Orientation.Vertical:
                return str(section)

        return super().headerData(section, orientation, role)

def _get_series_missing_ranges(series: pd.Series) -> pd.DataFrame:
    missing = series.isnull()
    consecutive_missing = (
        list(map(lambda x: x[0], list(g)))
        for k, g in itertools.groupby(enumerate(missing), lambda x: x[1])
        if k)

    return pd.DataFrame(
        ((series.index[x[0]], series.index[x[-1]], len(x)) for x in consecutive_missing),
        columns=['start', 'end', 'length'])

def _get_missing_ranges(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        column: _get_series_missing_ranges(data[column])
        for column in data.columns}
