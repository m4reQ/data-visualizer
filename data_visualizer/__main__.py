import sys

from PyQt6.QtWidgets import QApplication

from data_visualizer.ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    result = app.exec()
    sys.exit(result)
