import functools
import os
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QLabel,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QStatusBar,
    QStyleFactory,
    QWidget,
)

from .imageprocess import Imageprocess
from .imagestack import Imagestack
from .roicollection import Roicollection
from .subtractor import Subtractor
from .utils import dump_json, fileScanner


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

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 405)
        # set contral widget
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        # gui locker
        self.checkBox_lock = QCheckBox(self.centralwidget)
        self.checkBox_lock.setGeometry(QtCore.QRect(100, 10, 91, 25))
        self.checkBox_lock.setFont(self.getFont(pointsize=12, bold=False, weight=50))
        self.checkBox_lock.setObjectName("checkBox_lock")

        self.checkBox_json = QCheckBox(self.centralwidget)
        self.checkBox_json.setGeometry(QtCore.QRect(100, 50, 91, 25))
        self.checkBox_json.setFont(self.getFont(pointsize=12, bold=False, weight=50))
        self.checkBox_json.setObjectName("json")

        self.checkBox_prenormalized = QCheckBox(self.centralwidget)
        self.checkBox_prenormalized.setGeometry(QtCore.QRect(100, 90, 91, 25))
        self.checkBox_prenormalized.setFont(
            self.getFont(pointsize=12, bold=False, weight=50)
        )
        self.checkBox_prenormalized.setObjectName("prenormalized")

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

        # open button
        self.pushButton_open = QPushButton(self.centralwidget)
        self.pushButton_open.setGeometry(QtCore.QRect(10, 10, 81, 57))
        self.pushButton_open.setFont(self.getFont(bold=True, weight=75))
        self.pushButton_open.setObjectName("pushButton_open")

        # set_roi button
        self.pushButton_set_roi = QPushButton(self.centralwidget)
        self.pushButton_set_roi.setGeometry(QtCore.QRect(10, 75, 81, 57))
        self.pushButton_set_roi.setFont(self.getFont(bold=True, weight=75))
        self.pushButton_set_roi.setObjectName("pushButton_set_roi")

        # process_window button
        self.pushButton_process_window = QPushButton(self.centralwidget)
        self.pushButton_process_window.setGeometry(QtCore.QRect(10, 235, 101, 57))
        self.pushButton_process_window.setFont(self.getFont(bold=True, weight=75))
        self.pushButton_process_window.setObjectName("pushButton_process_window")

        # start process bottum
        self.pushButton_start_processing = QPushButton(self.centralwidget)
        self.pushButton_start_processing.setGeometry(QtCore.QRect(10, 300, 101, 57))
        self.pushButton_start_processing.setFont(self.getFont(bold=True, weight=75))
        self.pushButton_start_processing.setObjectName("pushButton_start_processing")

        # save process bottum
        self.pushButton_save = QPushButton(self.centralwidget)
        self.pushButton_save.setGeometry(QtCore.QRect(130, 300, 101, 57))
        self.pushButton_save.setFont(self.getFont(bold=True, weight=75))
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
        self.spinBox_columns.setValue(self.__droicolnum)
        self.spinBox_columns.setObjectName("spinBox_columns")

        # roi rows number
        self.spinBox_rows = QSpinBox(self.centralwidget)
        self.spinBox_rows.setGeometry(QtCore.QRect(390, 45, 48, 25))
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
        self.doubleSpinBox_threshold.setMaximum(255)
        self.doubleSpinBox_threshold.setValue(self.__dthreshold)
        self.doubleSpinBox_threshold.setDecimals(0)
        self.doubleSpinBox_threshold.setObjectName("doubleSpinBox_threshold")

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

        label_font = self.getFont(pointsize=10, bold=True, weight=75)
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
                self, name, self.getLabel(self.centralwidget, geo, label_font, name)
            )

        # format all buttons text
        self.retranslateUi(self)

        # synchronize the left-top x and left-top y.
        self.doubleSpinBox_x.editingFinished.connect(self.horizontalSlider_value_update)
        self.doubleSpinBox_y.editingFinished.connect(self.horizontalSlider_value_update)

        for slider in MainWindow.findChild(QWidget).children():
            if "horizontalSlider" in slider.objectName():
                slider.actionTriggered.connect(self.doubleSpinBox_value_update)
                slider.sliderReleased.connect(self.doubleSpinBox_value_update)

        for obj in MainWindow.findChild(QWidget).children():
            objname = obj.objectName()
            if "doubleSpinBox" in objname or "spinBox" in objname:
                obj.valueChanged.connect(self.setroi)

        # set open and roi buttons
        self.pushButton_open.clicked.connect(self.askdirectory)
        self.pushButton_set_roi.clicked.connect(self.setroi)

        # run button
        self.pushButton_start_processing.clicked.connect(self.startprocess)
        # save button
        self.pushButton_save.clicked.connect(self.savedata)

        # comboBox_matrix
        self.comboBox_matrix.currentIndexChanged["QString"].connect(
            self.get_row_and_col
        )
        # change style
        self.styleComboBox.activated[str].connect(self.changeStyle)

        # lock all buttons except lock buttom
        for obj in self.findChild(QWidget).children():
            if "checkBox_lock" in obj.objectName():
                continue
            self.checkBox_lock.toggled.connect(obj.setDisabled)

        self.checkBox_json.toggled.connect(self.setroi)
        self.checkBox_prenormalized.toggled.connect(self.showNormState)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def showNormState(self):
        prenorm = self.checkBox_prenormalized.isChecked()
        if prenorm:
            msg = "[SYSTEM] Images will be normalized before subtraction"
            self.showMessage(msg)
        else:
            self.statusbar.showMessage("")

    def getFont(self, fonttype="Helvetica", pointsize=None, bold=None, weight=None):
        font = QtGui.QFont(fonttype)
        if pointsize is not None:
            font.setPointSize(pointsize)
        if bold is not None:
            font.setBold(bold)
        if weight is not None:
            font.setWeight(weight)
        return font

    def getLabel(self, parent, geometry, font, name):
        label = QLabel(parent)
        label.setGeometry(QtCore.QRect(*geometry))
        label.setFont(font)
        label.setObjectName(name)
        return label

    def retranslateUi(self, MainWindow):
        _translate = functools.partial(QtCore.QCoreApplication.translate, "MainWindow")
        MainWindow.setWindowTitle(_translate("Processor"))
        self.checkBox_lock.setText(_translate("Lock"))
        self.checkBox_json.setText(_translate("Roi"))
        self.checkBox_prenormalized.setText(_translate("Pre-normalized"))
        self.pushButton_open.setText(_translate("Open"))
        self.pushButton_set_roi.setText(_translate("Set Roi"))
        self.pushButton_process_window.setText(_translate("Process\n" "Window"))
        self.pushButton_start_processing.setText(_translate("Start\n" "Processing"))
        self.pushButton_save.setText(_translate("Save"))
        self.menuImage_Processor.setTitle(_translate("Image Processor"))

        # label text
        for i, (txt, _) in enumerate(self.label_geometries):
            name = f"label_{i}"
            getattr(self, name).setText(_translate(txt))

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        QApplication.setPalette(self.originalPalette)

    def showMessage(self, msg):
        self.statusbar.showMessage(msg)
        print(msg)

    def showError(self, msg):
        QMessageBox.information(self, None, msg, QMessageBox.Ok)
        self.showMessage(msg)

    def askdirectory(self):
        if self.ims is not None:
            self.ims.clear()
        dialog = QFileDialog(self)
        dirs = dialog.getExistingDirectory()
        if not dirs:
            self.showError("[SYSTEM] The directory is not selected")
            return
        self.imagedir = Path(dirs)
        self.roijsonfile = None
        self.jpgfilenamelist = []
        self.showMessage(f"[SYSTEM] The directory is selected at: {str(self.imagedir)}")
        for file in fileScanner(self.imagedir):
            if file.name.endswith((".jpg", ".jpeg")):
                self.jpgfilenamelist.append(file.name)
            elif file.name.endswith(".json"):
                self.roijsonfile = file.path
                self.showMessage(f"[SYSTEM] Find a JSON file: {file.name}")

        if len(self.jpgfilenamelist) > 0:
            if not self.ims:
                self.ims = Imagestack(self)
            self.showMessage(f"Image numbers: {len(self.jpgfilenamelist):d}")
            self.ims.setdir(self.imagedir, self.jpgfilenamelist)
            self.endslice = len(self.jpgfilenamelist) - 1
            self.spinBox_start.setValue(0)

            tempimage = self.ims[0]
            max_y, max_x, _ = tempimage.shape
            self.doubleSpinBox_x.setMaximum(max_x)
            self.horizontalSlider_x.setMaximum(max_x)
            self.doubleSpinBox_y.setMaximum(max_y)
            self.horizontalSlider_y.setMaximum(max_y)
            self.spinBox_end.setValue(len(self.jpgfilenamelist) - 1)
        else:
            self.showMessage("[SYSTEM] The directory does not have any jpg files")
        self.update

    def doubleSpinBox_value_update(self, **kwargs):
        x = self.horizontalSlider_x.value()
        y = self.horizontalSlider_y.value()
        self.doubleSpinBox_x.setValue(x)
        self.doubleSpinBox_y.setValue(y)
        if isinstance(self.ims, type(Imagestack)):
            self.setroi()
        self.update

    def horizontalSlider_value_update(self, **kwargs):
        x = self.doubleSpinBox_x.value()
        y = self.doubleSpinBox_y.value()
        self.horizontalSlider_x.setValue(int(x))
        self.horizontalSlider_y.setValue(int(y))
        if isinstance(self.ims, type(Imagestack)):
            self.setroi()
        self.update

    def get_row_and_col(self):
        col, row = tuple(map(int, self.comboBox_matrix.currentText().split(" x ")))
        self.spinBox_columns.setValue(col)
        self.spinBox_rows.setValue(row)
        if self.ims is not None:
            tempimage = self.ims[0]
            imageshape = tempimage.shape
            iwidth = imageshape[1]
            iheight = imageshape[0]
            xinterval = iwidth / (float(col) + 0.36)
            yinterval = iheight / (float(row) + 0.36)
            self.horizontalSlider_value_update(xinterval=xinterval, yinterval=yinterval)
            self.doubleSpinBox_value_update(xinterval=xinterval, yinterval=yinterval)
            self.setroi()
        self.update

    def setroi(self):
        self.roicol = Roicollection(parent=self)
        if self.checkBox_json.isChecked():
            if self.roijsonfile:
                self.roicol.read_json(self.roijsonfile)
                roisarg = self.roicol.roidict.get("roisarg")
                if roisarg:
                    roicolnum = int(roisarg["roicolnum"])
                    roirownum = int(roisarg["roirownum"])
                    roiintervalx = float(roisarg["roiintervalx"])
                    roiintervaly = float(roisarg["roiintervaly"])
                    x = int(roisarg["x"])
                    y = int(roisarg["y"])
                    width = int(roisarg["width"])
                    height = int(roisarg["height"])
                    radianrot = roisarg["radianrot"]
                    rotate = radianrot * 180 / np.pi

                    self.spinBox_columns.setValue(roicolnum)
                    self.spinBox_rows.setValue(roirownum)
                    self.doubleSpinBox_x_interval.setValue(roiintervalx)
                    self.doubleSpinBox_y_interval.setValue(roiintervaly)
                    self.doubleSpinBox_x.setValue(x)
                    self.horizontalSlider_x.setValue(x)
                    self.doubleSpinBox_y.setValue(y)
                    self.horizontalSlider_y.setValue(y)
                    self.doubleSpinBox_width.setValue(width)
                    self.doubleSpinBox_height.setValue(height)
                    self.doubleSpinBox_rotate.setValue(rotate)

        else:
            # self.roilist = []
            # roi column num
            roicolnum = int(self.spinBox_columns.value())
            # roi row num
            roirownum = int(self.spinBox_rows.value())
            # roi interval x
            roiintervalx = float(self.doubleSpinBox_x_interval.value())
            # roi interval y
            roiintervaly = float(self.doubleSpinBox_y_interval.value())
            # topleft
            x = int(self.doubleSpinBox_x.value())
            y = int(self.doubleSpinBox_y.value())
            width = int(self.doubleSpinBox_width.value())
            height = int(self.doubleSpinBox_height.value())
            radianrot = np.pi * float(self.doubleSpinBox_rotate.value()) / 180

            roisarg = (
                roicolnum,
                roirownum,
                roiintervalx,
                roiintervaly,
                x,
                y,
                width,
                height,
                radianrot,
            )
            self.roicol.setrois(*roisarg)
        if self.ims:
            self.ims.showrois(self.roicol)

    def savedata(self):
        if self.imagedir is None:
            self.showError("[SYSTEM] The directory is not selected")
            return
        if self.outputdata is not None:
            # np.savetxt(os.path.join(self.imagedir, "np_area.csv"), self.outputdata, delimiter = ",", fmt = "%d")
            df = pd.DataFrame(
                self.outputdata, columns=["Area" for a in range(self.roicol.getlen())]
            )
            df.to_csv(os.path.join(self.imagedir, "area.csv"), index=False)
            self.showMessage("[SYSTEM] area.csv was saved at %s" % self.imagedir)

        if self.roicol is not None:
            if len(self.roicol.roidict) != 0:
                try:
                    jsonpath = os.path.join(self.imagedir, "Roi.json")
                    dump_json(jsonpath, self.roicol.roidict)
                    self.showMessage(
                        "[SYSTEM] Roi.json was saved at %s" % self.imagedir
                    )
                except Exception as e:
                    self.showMessage("[ERROR] %s" % e)

    def showprocesswindow(self):
        self.startslice = int(self.spinBox_start.value())
        self.endslice = int(self.spinBox_end.value())
        self.threshold = float(self.doubleSpinBox_threshold.value())
        self.slicestep = int(self.spinBox_step.value())

        self.subtwindowname = "subtmed"
        cv2.startWindowThread()
        cv2.namedWindow(self.subtwindowname, cv2.WINDOW_NORMAL)
        if self.ims is not None:
            tempimage = self.ims[0]
            empty_img = np.zeros(tempimage.shape)
            cv2.imshow(self.subtwindowname, empty_img)
        cv2.createTrackbar(
            "slice", self.subtwindowname, 0, self.endslice, self.showsubtmedimg
        )
        pre_normalized = self.checkBox_prenormalized.isChecked()
        self.ip = Imageprocess(
            self,
            windowname=self.subtwindowname,
            threshold=self.threshold,
            slicestep=self.slicestep,
            normalized=pre_normalized,
        )

    def startprocess(self):
        if self.jpgfilenamelist:
            """
            self.slicestartstr = self.boxstart.get()
            self.sliceendstr = self.boxend.get()
            self.startslice = int(self.slicestartstr)
            self.endslice = int(self.sliceendstr)
            print(str(self.startslice)+":"+str(self.endslice))
            self.threshold = float(self.boxthreshold.get())

            self.subtwindowname = "subtmed"
            cv2.startWindowThread()
            cv2.namedWindow(self.subtwindowname, cv2.WINDOW_NORMAL)
            cv2.createTrackbar('slice',self.subtwindowname,
                                  0,self.endslice, self.showsubtmedimg)
            self.ip = Imageprocess(self, windowname = self.subtwindowname,
                                   threshold = self.threshold)
            #self.ip = Imageprocess(self, save = True)
            """
            self.showMessage("[SYSTEM] Processing...")
            self.showprocesswindow()
            self.outputdata = None
            self.ip.start()
            self.checkBox_lock.setCheckState(2)
            # print(len(self.outputdata))
            # self.ip.join()

    def showsubtmedimg(self, n):
        # if self.ip.is_alive():
        #    print("ip is alive")
        # """
        if not self.ip.is_alive():
            # print("ip is Not alive")
            self.threshold = float(self.doubleSpinBox_threshold.value())
            # print(n)
            # print(self.threshold)
            if n < self.ims.nslice - 1:
                prenorm = self.checkBox_prenormalized.isChecked()
                subtractor = Subtractor(prenorm)
                subtractor.setinitialimage(self.ims[n])
                subimage = subtractor.subtractfromholdingimage(self.ims[n + 1])
                subtmedimg = cv2.medianBlur(subimage, 5)
                # print(subtmedimg.shape)#(768,1024,3)
                olimg = self.overlaythreshold(subtmedimg, self.threshold)
                # cv2.imshow(self.subtwindowname, subtmedimg)
                cv2.imshow(self.subtwindowname, olimg)
                # cv2.setTrackbarPos('slice',self.windowname,i)

    def overlaythreshold(self, img, val):
        # colimg = np.zeros(img.shape, dtype = np.uint8)
        threshold = 127 - val * 12.8
        # print(threshold)
        retval, binaryimg = cv2.threshold(
            img[:, :, 2], threshold, 1, cv2.THRESH_BINARY_INV
        )
        # mask = cv2.inRange(img, np.array([0,0,0]),np.array([val,val,val]))
        # red channel =2, green =1, blue = 0
        # colimg[:,:,2][binaryimg == 1] = 255
        img[:, :, 2][binaryimg.astype(bool)] = 255
        # colimg[:,:,2][img[:,:,2] < threshold] = 255
        # colimg[img < val] = [[[0,0,255]]]
        # return colimg + img
        return img

    def toggle_l(self):
        # self.writeinlog("toggle1")
        # global cause error only made a exe with cx_freeze?
        # global onofftoggle1
        # self.writeinlog(str(self.onofftoggle1))
        if self.startstoptoggle_l:
            self.button_l.config(text="Stop live", bg="red")
            self.startstoptoggle_l = False
            self.livestart()
        else:
            self.button_l.config(text="Live", bg=self.orignalbuttoncolor_l)
            self.startstoptoggle_l = True
            self.livestop()
