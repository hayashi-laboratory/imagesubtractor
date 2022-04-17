from turtle import window_width
from typing import Callable, Optional
import cv2
import numpy as np

from PySide2 import QtGui, QtWidgets, QtCore


class ImageViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.data = None
        self.pixel = QtGui.QPixmap()
        self.__scene = QtWidgets.QGraphicsScene(self)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def set_image(self, src: np.ndarray, win_width :int= None, win_height:int = None):
        if src.ndim == 2:
            img = cv2.cvtColor(src, cv2.COLOR_GRAY2RGB)
        elif src.ndim == 3:
            img = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
        else:
            raise TypeError("Image type error")

        h, w, _ = img.shape
        self.data = img
        win_width = win_width if win_width is not None else h
        win_height = win_height if win_height is not None else h
        qimg = QtGui.QImage(self.data.data, w, h, self.data.ndim * w, QtGui.QImage.Format_RGB888).scaled(win_width, win_height, QtCore.Qt.KeepAspectRatio)
        item = QtWidgets.QGraphicsPixmapItem(self.pixel.fromImageInPlace(qimg))
        item.setPos(0, 0)
        self.__scene.addItem(item)
        self.__scene.setSceneRect(0, 0, win_width, win_height)
        self.setScene(self.__scene)
        self.resize(win_width, win_height)
        self.update()


class ProcessWindow(QtWidgets.QWidget):
    def __init__(self, parent=None, processnum: int = 1000):
        super().__init__(parent=parent)
        self.setWindowTitle("Processing...")
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setMaximum(processnum)

        self.progress = QtWidgets.QProgressBar(self)
        self.valueChanged = self.slider.valueChanged
        self.canvas = ImageViewer(self)
        layout.addWidget(self.slider)
        layout.addWidget(self.canvas)
        layout.addWidget(self.progress)
        self.show()
    
    def setMaximum(self, max_val:int):
        self.slider.setMaximum(max_val)
        self.progress.setMaximum(max_val)

    @property
    def value(self)->int:
        return self.slider.value()

    def imshow(self, image: np.ndarray, pos: int = None):
        if isinstance(pos, int):
            self.slider.setValue(pos)
        self.canvas.set_image(image, self.width(), self.height())
        self.update()


class ProcessWindowCV:
    def __init__(
        self,
        total: int,
        winname: str = "Processing...",
        onChange: Optional[Callable] = None,
    ):
        self.total = total
        self.winname = winname
        self.barname = "slice"
        self.onChange = onChange if callable(onChange) else self.__nothing

    def __nothing(self, *args, **kwargs):
        pass

    def __enter__(self):
        self.destroy()
        self.__running = False
        cv2.namedWindow(self.winname, cv2.WINDOW_NORMAL)
        cv2.startWindowThread()
        return self

    def __exit__(self, *args, **kwargs):
        self.destroy()

    def destroy(self):
        try:
            cv2.waitKey(1)
            cv2.destroyWindow(self.winname)
            cv2.waitKey(1)
        except cv2.error:
            pass

    def imshow(self, image: np.ndarray, pos: int):
        cv2.imshow(self.winname, image)
        if not self.__running:
            # create tracker bar after showing an image
            self.onChange
            cv2.createTrackbar(self.barname, self.winname, 0, self.total, self.onChange)
            self.__running = True

        cv2.setTrackbarPos(self.winname, image, pos)
