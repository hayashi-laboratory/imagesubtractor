from pathlib import Path
from typing import Any, Dict, Optional

import cv2
import numpy as np
from PySide2 import QtCore
from PySide2.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStyleFactory,
    QWidget,
)

from .mainwindowUI import MainWindowUI
from .process import (
    Contrast,
    ImageProcessQWorker,
    Imagestack,
    ParallelSubtractor,
    RoiCollection,
    Subtractor,
)
from .utils import dump_json


class MainWindow(QMainWindow, MainWindowUI):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.ims = None
        self.outputdata = None
        self.roijsonfile = None
        self.roicol = None
        self.cr = Contrast()
        self.setup_widget_events()

    def setup_widget_events(self):

        # self.centralwidget.keyPressed.connect(self.on_key)
        # synchronize the left-top x and left-top y.
        self.doubleSpinBox_x.editingFinished.connect(self.horizontalSlider_value_update)
        self.doubleSpinBox_y.editingFinished.connect(self.horizontalSlider_value_update)

        for slider in self.findChild(QWidget).children():
            if "horizontalSlider" in slider.objectName():
                slider.actionTriggered.connect(self.doubleSpinBox_value_update)
                slider.sliderReleased.connect(self.doubleSpinBox_value_update)

        for obj in self.findChild(QWidget).children():
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

        # bind step with slider
        self.spinBox_step.editingFinished.connect(
            lambda: self.view.setStep(self.slicestep)
        )

        # lock all buttons except lock buttom
        for obj in self.findChild(QWidget).children():
            if "checkBox_lock" in obj.objectName():
                continue
            self.checkBox_lock.toggled.connect(obj.setDisabled)
        self.checkBox_lock.toggled.connect(self.view.setDisabled)
        self.checkBox_lock.toggled.connect(self.contrast_view.setDisabled)
        self.checkBox_json.toggled.connect(self.setroi)
        self.checkBox_prenormalized.toggled.connect(self.showNormState)

        QtCore.QMetaObject.connectSlotsByName(self)

    def showNormState(self):
        if self.checkBox_prenormalized.isChecked():
            msg = "[SYSTEM] Images will be normalized before subtraction"
            self.show_message(msg)

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))
        QApplication.setPalette(self.originalPalette)

    def show_message(self, msg) -> "MainWindow":
        self.statusbar.showMessage(msg)
        print(msg)
        return self

    def showError(self, msg) -> "MainWindow":
        QMessageBox.information(self, None, msg, QMessageBox.Ok)
        return self.show_message(msg)

    def askdirectory(self) -> "MainWindow":
        dialog = QFileDialog(self)
        dirs = dialog.getExistingDirectory()
        if not dirs:
            self.showError("[SYSTEM] The directory is not selected")
            return
        jsonfiles = (f for f in Path(dirs).glob("*.json") if not f.name.startswith("."))
        self.roijsonfile = max(jsonfiles, key=lambda f: f.name, default=None)
        self.show_message(f"[SYSTEM] The directory is selected at: {str(dirs)}")
        self.ims = Imagestack().set_folder(dirs)

        if not len(self.ims):
            self.ims = None
            self.cr = None
            self.show_message(
                "[SYSTEM] The directory does not have any jpg files"
            ).update
            return self

        return (
            self.reset_value_boundary()
            .setview()
            .setcontrast()
            .setroi()
            .show_message(f"Image numbers: {len(self.ims)}")
        )

    def setcontrast(self) -> "MainWindow":
        def set_contrast_view_callback():
            self.cr.set_range(*self.contrast_view.get_range())
            self.draw_view()

        self.contrast_view.update_canvas = set_contrast_view_callback

        return self

    def setview(self) -> "MainWindow":
        if self.ims is None or not len(self.ims):
            return self
        self.view.setMaximum(len(self.ims) - 1)
        self.view.slider.setTickInterval(len(self.ims) // 10)
        img = self.ims.read_image(0)
        H, W = img.shape[:2]
        self.resize(640 + W + 20, max(H + 75, 610))
        self.view.setGeometry(QtCore.QRect(640, 20, W, H + 50))
        self.progressbar.setGeometry(QtCore.QRect(650, H + 75, W - 10, 35))
        self.view.imshow(self.roicol.draw_rois(img), 0)
        self.checkBox_sub.clicked.connect(self.draw_view)
        self.view.valueChanged.connect(self.draw_view)
        return self

    def draw_view(self):
        self.set_text_num(self.view.value)
        img = self.ims.read_image(self.view.value)
        self.contrast_view.imshow(self.cr.draw_histogram(img))
        if self.cr.adjusted:
            img = self.cr.draw_contrast(img)
        if self.show_subtract:
            binary = np.zeros_like(img, dtype=np.uint8)
            if self.view.value >= self.slicestep:
                pre = self.ims.read_image(self.view.value - self.slicestep)
                _, _, binary = (
                    Subtractor(self.threshold, self.normalized)
                    .set_image(pre, 0)
                    .set_image(img, 1)
                    .subtract()
                    .median_blur()
                    .threshold_binarize()
                    .get_results()
                )
            img = binary.astype(np.uint8) * 255
        img_roi = self.roicol.draw_rois(img)
        self.view.imshow(img_roi)

    def set_text_num(self, num: int):
        if self.ims is None or not len(self.ims):
            return
        self.num_window.setText(f"{num+1}/{len(self.ims)}")

    def reset_value_boundary(self) -> "MainWindow":
        total = len(self.ims) - 1
        x_max = self.ims.img_width
        y_max = self.ims.img_height
        self.doubleSpinBox_x.setMaximum(x_max)
        self.horizontalSlider_x.setMaximum(x_max)
        self.doubleSpinBox_y.setMaximum(y_max)
        self.horizontalSlider_y.setMaximum(y_max)

        self.spinBox_start.setValue(0)
        self.spinBox_end.setValue(total)
        self.spinBox_start.setMaximum(total)
        self.spinBox_end.setMaximum(total)
        self.spinBox_step.setMaximum(total - 1)
        return self

    def doubleSpinBox_value_update(self, **kwargs):
        x = self.horizontalSlider_x.value()
        y = self.horizontalSlider_y.value()
        self.doubleSpinBox_x.setValue(x)
        self.doubleSpinBox_y.setValue(y)
        self.setroi().update

    def horizontalSlider_value_update(self, **kwargs):
        x = self.doubleSpinBox_x.value()
        y = self.doubleSpinBox_y.value()
        self.horizontalSlider_x.setValue(int(x))
        self.horizontalSlider_y.setValue(int(y))
        self.setroi().update

    def show_roi(self, event=None) -> "MainWindow":
        if self.ims is None or not len(self.ims):
            return self

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

    def setroi(self) -> "MainWindow":
        if getattr(self, "ims", None) is None:
            return

        if self.checkBox_json.isChecked() and self.roijsonfile:
            self.roicol = RoiCollection.from_json(self.roijsonfile)
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
            roi_kws = self.get_rois_kws()
            ymax, xmax = None, None
            if self.ims:
                xmax = self.ims.img_width
                ymax = self.ims.img_height

            roi_kws.update(xmax=xmax, ymax=ymax)
            self.roicol = RoiCollection().set_rois(**roi_kws)

        self.draw_view()
        return self

    def get_rois_kws(self) -> Dict[str, Any]:
        return dict(
            roicolnum=int(self.spinBox_columns.value()),
            roirownum=int(self.spinBox_rows.value()),
            roiintervalx=float(self.doubleSpinBox_x_interval.value()),
            roiintervaly=float(self.doubleSpinBox_y_interval.value()),
            x=int(self.doubleSpinBox_x.value()),
            y=int(self.doubleSpinBox_y.value()),
            box_width=int(self.doubleSpinBox_width.value()),
            box_height=int(self.doubleSpinBox_height.value()),
            radianrot=np.pi * float(self.doubleSpinBox_rotate.value()) / 180,
        )

    def savedata(self):
        if self.imagedir is None:
            self.showError("[SYSTEM] The directory is not selected")
            return

    def startprocess(self):
        if not self.ims or not len(self.ims):
            return

        self.checkBox_lock.setCheckState(QtCore.Qt.CheckState.Checked)
        processnum, task = self.ims.create_task_queue(
            self.startslice, self.endslice, self.slicestep
        )
        self.outputdata = np.zeros((processnum, len(self.roicol)), dtype=int)
        subtractors = ParallelSubtractor().setup_workers(
            processnum=processnum,
            task=task,
            roicollection=self.roicol.copy(),
            threshold=self.threshold,
            normalized=self.normalized,
            saveflag=False,
        )
        self.__roi_mask = self.roicol.draw_rois(np.zeros_like(self.ims.read_image(0)))
        dump_json(self.ims.homedir / "Roi.json", self.roicol.roidict)
        self.show_message("[SYSTEM] Roi.json was saved at %s" % self.imagedir)
        self.progressbar.setRange(0, processnum)
        self.progressbar.show()
        qt = ImageProcessQWorker(self, subtractors, self.ims.homedir)
        qt.start()
        self.__processnum = processnum

        def finish():
            self.checkBox_lock.setCheckState(QtCore.Qt.CheckState.Unchecked)
            self.progressbar.hide()
            del self.__roi_mask
            del self.__processnum

        qt.process_result.connect(self.show_process)
        qt.finished.connect(finish)

    def show_process(self, task):
        if task is None:
            return
        i, image = task
        self.set_text_num(i)
        image = cv2.addWeighted(image, 1, self.__roi_mask, 1, 0)
        self.view.imshow(image)
        self.progressbar.setValue(i)

    def showsubtmedimg(self, n):
        if self.ip.is_alive():
            return

        if n < len(self.ims) - 2:
            _, blur, binary = (
                Subtractor(self.threshold, self.normalized)
                .set_image(self.ims.read_image(n), 0)
                .set_image(self.ims.read_image(n + 1), 1)
                .subtract()
                .median_blur()
                .threshold_binarize()
                .get_results()
            )
            blur[binary][2] = 255
