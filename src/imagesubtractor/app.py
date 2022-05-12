#!/usr/bin/env python3
import os
import sys

from PySide2.QtCore import QLibraryInfo
from PySide2.QtWidgets import QApplication

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
    QLibraryInfo.PluginsPath
)


from imagesubtractor.mainwindow import MainWindow


def run_app(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    app = QApplication(argv)
    appUI = MainWindow()
    appUI.show()
    appUI.raise_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_app()