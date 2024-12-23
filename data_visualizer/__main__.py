import sys
import typing as t

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication

from data_visualizer.ui.main_window import MainWindow


def _load_stylesheet(theme: t.Literal['light'] | t.Literal['dark']) -> str:
    style = ''
    with open('./assets/styles/style_common.qss', 'r') as f:
        style = f.read()

    with open(f'./assets/styles/style_{theme}.qss', 'r') as f:
        style += f.read()

    return style


if __name__ == '__main__':
    settings = QSettings('m4reQ', 'data_visualizer')
    stylesheet = _load_stylesheet(settings.value('theme', 'light'))

    app = QApplication(sys.argv)
    # app.setStyleSheet(stylesheet)

    main_window = MainWindow(settings)
    main_window.show()

    app.exec()
