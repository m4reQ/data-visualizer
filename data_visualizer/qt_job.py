import typing as t

from PyQt6.QtCore import QObject, QRunnable, pyqtBoundSignal, pyqtSignal

TReturn = t.TypeVar('TReturn')
TParams = t.ParamSpec('TParams')

class JobSignals(QObject):
    error = pyqtSignal(Exception)
    finished = pyqtSignal(object)

class Job(QRunnable):
    def __init__(self,
                 fn: t.Callable[TParams, TReturn],
                 *args: TParams.args,
                 **kwargs: TParams.kwargs) -> None:
        super().__init__()

        self._signals = JobSignals()

        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @property
    def error(self) -> pyqtBoundSignal:
        return self._signals.error

    @property
    def finished(self) -> pyqtBoundSignal:
        return self._signals.finished

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as exc:
            self.error.emit(exc)
        else:
            self.finished.emit(result)
