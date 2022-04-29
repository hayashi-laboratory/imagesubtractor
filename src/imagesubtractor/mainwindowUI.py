import functools
from pathlib import Path
from typing import Optional

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import (
    QMainWindow,
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QLabel,
    QMenu,
    QMenuBar,
    QPushButton,
    QSlider,
    QSpinBox,
    QStatusBar,
    QStyleFactory,
    QWidget,
    QLineEdit,
)

from .widgets import ContrastWidget, SliderViewer


def qfont(
    fonttype="Helvetica",
    pointsize=None,
    bold=None,
    weight=None,
) -> QtGui.QFont:
    font = QtGui.QFont(fonttype)
    if pointsize is not None:
        font.setPointSize(pointsize)
    if bold is not None:
        font.setBold(bold)
    if weight is not None:
        font.setWeight(weight)
    return font


def qlabel(parent, geometry, font, name) -> QLabel:
    label = QLabel(parent)
    label.setGeometry(QtCore.QRect(*geometry))
    label.setFont(font)
    label.setObjectName(name)
    return label


class MainWindowUI:
    # default gui values
    __droiwidth = 78  # roi width
    __droiheight = 78  # roi height
    __droicolnum = 8  # roi column num
    __droirownum = 6  # roi row num
    __dtopleftx = 50  # roi top left x
    __dtoplefty = 49  # roi top left y
    __dintervalx = 130  # roi interval x
    __dintervaly = 130  # roi interval y
    __drotate = 0  # roi rotate degree
    __dthreshold = 2  # threshold
    __slicestep = 1  # step to process slice.

    def setupUi(self, MainWindow: QMainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 610)
        # set contral widget
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # gui locker
        self.checkBox_lock = QCheckBox(self.centralwidget)

        # QtCore.QRect(100, 10, 91, 30)
        self.checkBox_lock.setGeometry(QtCore.QRect(100, 90, 50, 25))
        self.checkBox_lock.setFont(qfont(pointsize=10, bold=False, weight=60))
        self.checkBox_lock.setObjectName("checkBox_lock")
        # tCore.QRect(100, 50, 91, 30)
        self.checkBox_json = QCheckBox(self.centralwidget)
        self.checkBox_json.setGeometry(QtCore.QRect(150, 90, 50, 25))
        self.checkBox_json.setFont(qfont(pointsize=10, bold=False, weight=60))
        self.checkBox_json.setObjectName("json")
        # QtCore.QRect(100, 90, 120, 25)
        self.checkBox_prenormalized = QCheckBox(self.centralwidget)
        self.checkBox_prenormalized.setGeometry(QtCore.QRect(200, 90, 120, 25))
        self.checkBox_prenormalized.setFont(qfont(pointsize=10, bold=False, weight=60))
        self.checkBox_prenormalized.setObjectName("prenormalized")
        # QtCore.QRect(100, 130, 91, 30)
        self.checkBox_sub = QCheckBox(self.centralwidget)
        self.checkBox_sub.setGeometry(QtCore.QRect(320, 90, 120, 25))
        self.checkBox_sub.setFont(qfont(pointsize=10, bold=False, weight=60))
        self.checkBox_sub.setObjectName("checkBox_sub")

        # gui palette
        self.originalPalette = QApplication.palette()
        # gui palette box
        self.styleComboBox = QComboBox(self.centralwidget)
        self.styleComboBox.setGeometry(QtCore.QRect(480, 50, 121, 25))
        styles = QStyleFactory.keys()
        self.styleComboBox.addItems(["Fusion"])
        self.styleComboBox.addItems(style for style in styles if "Fusion" not in style)
        self.styleLabel = QLabel("&Style:")
        self.styleLabel.setBuddy(self.styleComboBox)
        self.styleComboBox.setCurrentIndex(0)
        self.changeStyle("Fusion")
        self.styleComboBox.setObjectName("styleComboBox")

        # slide number display
        self.num_window = QLineEdit(self.centralwidget)
        self.num_window.setReadOnly(True)
        self.num_window.setGeometry(QtCore.QRect(470, 85, 141, 45))
        self.num_window.setDragEnabled(False)
        self.num_window.setAlignment(QtCore.Qt.AlignCenter)
        self.num_window.setFont(qfont(bold=True, weight=200, pointsize=16.0))
        self.num_window.setObjectName("num_window")
        self.num_window.setStyleSheet(
            "QLineEdit {background-color: rgb(12, 12, 12); color: rgb(19, 161, 14);}"
        )

        # open button
        self.pushButton_open = QPushButton(self.centralwidget)
        self.pushButton_open.setGeometry(QtCore.QRect(10, 10, 81, 57))
        self.pushButton_open.setFont(qfont(bold=True, weight=75))
        self.pushButton_open.setObjectName("pushButton_open")

        # set_roi button
        self.pushButton_set_roi = QPushButton(self.centralwidget)
        self.pushButton_set_roi.setGeometry(QtCore.QRect(10, 75, 81, 57))
        self.pushButton_set_roi.setFont(qfont(bold=True, weight=75))
        self.pushButton_set_roi.setObjectName("pushButton_set_roi")

        # process_window button
        self.pushButton_process_window = QPushButton(self.centralwidget)
        self.pushButton_process_window.setGeometry(QtCore.QRect(10, 235, 101, 57))
        self.pushButton_process_window.setFont(qfont(bold=True, weight=75))
        self.pushButton_process_window.setObjectName("pushButton_process_window")

        # start process bottum
        self.pushButton_start_processing = QPushButton(self.centralwidget)
        self.pushButton_start_processing.setGeometry(QtCore.QRect(10, 300, 101, 57))
        self.pushButton_start_processing.setFont(qfont(bold=True, weight=75))
        self.pushButton_start_processing.setObjectName("pushButton_start_processing")

        # save process bottum
        self.pushButton_save = QPushButton(self.centralwidget)
        self.pushButton_save.setGeometry(QtCore.QRect(130, 300, 101, 57))
        self.pushButton_save.setFont(qfont(bold=True, weight=75))
        self.pushButton_save.setObjectName("pushButton_save")

        # x-interval box
        self.doubleSpinBox_x_interval = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_x_interval.setGeometry(QtCore.QRect(420, 155, 68, 25))
        self.doubleSpinBox_x_interval.setDecimals(1)
        self.doubleSpinBox_x_interval.setMaximum(10000)
        self.doubleSpinBox_x_interval.setSingleStep(0.1)
        self.doubleSpinBox_x_interval.setValue(self.__dintervalx)
        self.doubleSpinBox_x_interval.setObjectName("doubleSpinBox_x_interval")

        # y-interval box
        self.doubleSpinBox_y_interval = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_y_interval.setGeometry(QtCore.QRect(420, 185, 68, 25))
        self.doubleSpinBox_y_interval.setDecimals(1)
        self.doubleSpinBox_y_interval.setMaximum(10000)
        self.doubleSpinBox_y_interval.setSingleStep(0.1)
        self.doubleSpinBox_y_interval.setValue(self.__dintervaly)
        self.doubleSpinBox_y_interval.setObjectName("doubleSpinBox_y_interval")

        # roi columns number
        self.spinBox_columns = QSpinBox(self.centralwidget)
        self.spinBox_columns.setGeometry(QtCore.QRect(390, 10, 48, 25))
        self.spinBox_columns.setMinimum(1)
        self.spinBox_columns.setValue(self.__droicolnum)
        self.spinBox_columns.setObjectName("spinBox_columns")

        # roi rows number
        self.spinBox_rows = QSpinBox(self.centralwidget)
        self.spinBox_rows.setGeometry(QtCore.QRect(390, 45, 48, 25))
        self.spinBox_rows.setMinimum(1)
        self.spinBox_rows.setValue(self.__droirownum)
        self.spinBox_rows.setObjectName("spinBox_rows")

        # roi width
        self.doubleSpinBox_width = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_width.setGeometry(QtCore.QRect(245, 10, 68, 25))
        self.doubleSpinBox_width.setAccelerated(True)
        self.doubleSpinBox_width.setProperty("showGroupSeparator", False)
        self.doubleSpinBox_width.setValue(self.__droiwidth)
        self.doubleSpinBox_width.setDecimals(1)
        self.doubleSpinBox_width.setMaximum(10000)
        self.doubleSpinBox_width.setSingleStep(0.1)
        self.doubleSpinBox_width.setObjectName("doubleSpinBox_width")

        # roi height
        self.doubleSpinBox_height = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_height.setGeometry(QtCore.QRect(245, 45, 68, 25))
        self.doubleSpinBox_height.setAccelerated(True)
        self.doubleSpinBox_height.setValue(self.__droiheight)
        self.doubleSpinBox_height.setDecimals(1)
        self.doubleSpinBox_height.setMaximum(10000)
        self.doubleSpinBox_height.setSingleStep(0.1)
        self.doubleSpinBox_height.setObjectName("doubleSpinBox_height")

        # set col and row number
        self.comboBox_matrix = QComboBox(self.centralwidget)
        self.comboBox_matrix.setGeometry(QtCore.QRect(480, 10, 121, 25))
        self.comboBox_matrix.setAutoFillBackground(False)
        self.comboBox_matrix.setEditable(False)
        _dcombinations = ["12 x 8", "8 x 6", "6 x 4", "4 x 3"]
        for item in _dcombinations:
            self.comboBox_matrix.addItem(item)
        self.comboBox_matrix.setCurrentIndex(1)
        self.comboBox_matrix.setObjectName("comboBox_matrix")

        # set rotation
        self.doubleSpinBox_rotate = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_rotate.setGeometry(QtCore.QRect(420, 215, 68, 25))
        self.doubleSpinBox_rotate.setSingleStep(0.05)
        self.doubleSpinBox_rotate.setMinimum(-180)
        self.doubleSpinBox_rotate.setMaximum(180)
        self.doubleSpinBox_rotate.setValue(self.__drotate)
        self.doubleSpinBox_rotate.setObjectName("doubleSpinBox_rotate")

        # x position box
        self.doubleSpinBox_x = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_x.setGeometry(QtCore.QRect(35, 155, 68, 25))
        self.doubleSpinBox_x.setDecimals(1)
        self.doubleSpinBox_x.setMaximum(2048)
        self.doubleSpinBox_x.setSingleStep(1)
        self.doubleSpinBox_x.setValue(self.__dtopleftx)
        self.doubleSpinBox_x.setObjectName("doubleSpinBox_x")

        # x position slider
        self.horizontalSlider_x = QSlider(self.centralwidget)
        self.horizontalSlider_x.setGeometry(QtCore.QRect(110, 155, 190, 25))
        self.horizontalSlider_x.setValue(self.__dtopleftx)
        self.horizontalSlider_x.setMaximum(2048)
        self.horizontalSlider_x.setTickInterval(1)
        self.horizontalSlider_x.setSingleStep(1)
        self.horizontalSlider_x.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_x.setObjectName("horizontalSlider_x")

        # y position box
        self.doubleSpinBox_y = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_y.setGeometry(QtCore.QRect(35, 185, 68, 25))
        self.doubleSpinBox_y.setDecimals(1)
        self.doubleSpinBox_y.setMaximum(2048)
        self.doubleSpinBox_y.setSingleStep(1)
        self.doubleSpinBox_y.setValue(self.__dtoplefty)
        self.doubleSpinBox_y.setObjectName("doubleSpinBox_y")

        # y position slider
        self.horizontalSlider_y = QSlider(self.centralwidget)
        self.horizontalSlider_y.setGeometry(QtCore.QRect(110, 185, 190, 25))
        self.horizontalSlider_y.setValue(self.__dtoplefty)
        self.horizontalSlider_y.setMaximum(2048)
        self.horizontalSlider_y.setTickInterval(1)
        self.horizontalSlider_y.setSingleStep(1)
        self.horizontalSlider_y.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider_y.setObjectName("horizontalSlider_y")

        self.doubleSpinBox_threshold = QDoubleSpinBox(self.centralwidget)
        self.doubleSpinBox_threshold.setGeometry(QtCore.QRect(420, 275, 68, 25))
        self.doubleSpinBox_threshold.setMinimum(-10)
        self.doubleSpinBox_threshold.setSingleStep(0.01)
        self.doubleSpinBox_threshold.setMaximum(10)
        self.doubleSpinBox_threshold.setValue(self.__dthreshold)
        self.doubleSpinBox_threshold.setDecimals(2)
        self.doubleSpinBox_threshold.setObjectName("doubleSpinBox_threshold")

        self.view = SliderViewer(self, 1000)
        self.view.setGeometry(QtCore.QRect(640, 20, 300, 400))
        self.view.setObjectName("view")

        self.progressbar = QtWidgets.QProgressBar(self)
        self.progressbar.setMaximumHeight(20)
        self.progressbar.hide()
        self.progressbar.setObjectName("progressbar")

        self.contrast_view = ContrastWidget(self)
        self.contrast_view.setGeometry(QtCore.QRect(30, 400, 270, 200))
        self.contrast_view.setObjectName("contrast_view")

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 640, 22))
        self.menubar.setObjectName("menubar")

        self.menuImage_Processor = QMenu(self.menubar)
        self.menuImage_Processor.setObjectName("menuImage_Processor")
        MainWindow.setMenuBar(self.menubar)

        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuImage_Processor.menuAction())

        self.spinBox_step = QSpinBox(self.centralwidget)
        self.spinBox_step.setGeometry(QtCore.QRect(420, 245, 68, 25))
        self.spinBox_step.setValue(self.__slicestep)
        self.spinBox_step.setMinimum(1)
        self.spinBox_step.setMaximum(100000)
        self.spinBox_step.setObjectName("spinBox_step")

        self.spinBox_start = QSpinBox(self.centralwidget)
        self.spinBox_start.setGeometry(QtCore.QRect(420, 305, 68, 25))
        self.spinBox_start.setMaximum(100000)
        self.spinBox_start.setObjectName("spinBox_start")

        self.spinBox_end = QSpinBox(self.centralwidget)
        self.spinBox_end.setGeometry(QtCore.QRect(420, 335, 68, 25))
        self.spinBox_end.setMaximum(100000)
        self.spinBox_end.setObjectName("spinBox_end")

        label_font = qfont(pointsize=10, bold=True, weight=75)
        self.label_geometries = [
            ("Width:", (190, 10, 43, 25)),
            ("Height:", (190, 45, 51, 25)),
            ("Columns:", (320, 10, 60, 25)),
            ("Rows:", (320, 45, 60, 25)),
            ("X Interval:", (340, 155, 73, 25)),
            ("Y Interval:", (340, 185, 73, 25)),
            ("X:", (15, 155, 25, 25)),
            ("Y:", (15, 185, 25, 25)),
            ("Rotate:", (340, 215, 73, 25)),
            ("Step:", (340, 245, 73, 25)),
            ("Threshold:", (340, 275, 73, 25)),
            ("Start:", (340, 305, 73, 25)),
            ("End:", (340, 335, 73, 25)),
        ]

        for i, (_, geo) in enumerate(self.label_geometries):
            name = f"label_{i}"
            setattr(
                self,
                name,
                qlabel(self.centralwidget, geo, label_font, name),
            )

        # format all buttons text
        self.retranslateUi(self)

    def retranslateUi(self, MainWindow):
        _translate = functools.partial(QtCore.QCoreApplication.translate, "MainWindow")
        MainWindow.setWindowTitle(_translate("Processor"))
        self.checkBox_lock.setText(_translate("Lock"))
        self.checkBox_json.setText(_translate("Roi"))
        self.checkBox_prenormalized.setText(_translate("Pre-normalized"))
        self.checkBox_sub.setText(_translate("show subtract"))
        self.pushButton_open.setText(_translate("Open"))
        self.pushButton_set_roi.setText(_translate("Set Roi"))
        self.pushButton_process_window.setText(_translate("Process\n" "Window"))
        self.pushButton_start_processing.setText(_translate("Start\n" "Processing"))
        self.pushButton_save.setText(_translate("Save"))
        self.menuImage_Processor.setTitle(_translate("Image Processor"))

        for i, (txt, _) in enumerate(self.label_geometries):
            name = f"label_{i}"
            getattr(self, name).setText(_translate(txt))

    @property
    def threshold(self):
        return float(self.doubleSpinBox_threshold.value())

    @property
    def imagedir(self) -> Optional[Path]:
        if self.ims is None:
            return None
        return self.ims.homedir

    @property
    def startslice(self) -> int:
        return int(self.spinBox_start.value())

    @property
    def endslice(self) -> int:
        return int(self.spinBox_end.value())

    @property
    def slicestep(self) -> int:
        return int(self.spinBox_step.value())

    @property
    def normalized(self) -> bool:
        return self.checkBox_prenormalized.isChecked()

    @property
    def show_subtract(self) -> bool:
        return self.checkBox_sub.isChecked()

    # def on_key(self, event):
    #     if self.checkBox_lock.isChecked():
    #         return

    #     if event.key() in (QtCore.Qt.Key_Q, QtCore.Qt.Key_Esc):
    #         self.close()
    #         return
    #     # test for a specific key
    #     if event.key() == QtCore.Qt.Key_O:
    #         self.askdirectory()
    #         return

    #     if self.ims is not None:
    #         increment = 0
    #         if event.key() == QtCore.Qt.Key_A:
    #             increment = -1

    #         elif event.key() == QtCore.Qt.Key_D:
    #             increment = 1
