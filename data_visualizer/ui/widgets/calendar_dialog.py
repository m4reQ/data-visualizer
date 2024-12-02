import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCalendarWidget, QDialog, QWidget


class CalendarDialog(QDialog):
    @staticmethod
    def get_date(title: str,
                 start_date: datetime.date,
                 end_date: datetime.date,
                 current_date: datetime.date,
                 parent: QWidget | None = None) -> datetime.date:
        win = CalendarDialog(title, start_date, end_date, current_date, parent)
        win.exec()

        return win.get_selected_date()

    def __init__(self,
                 title: str,
                 start_date: datetime.date,
                 end_date: datetime.date,
                 current_date: datetime.date,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowTitle(title)

        self._calendar = QCalendarWidget(self)
        self._calendar.setDateRange(start_date, end_date)
        self._calendar.setSelectedDate(current_date)

        self.setFixedSize(self._calendar.sizeHint())

    def get_selected_date(self) -> datetime.date:
        return self._calendar.selectedDate().toPyDate()
