from PySide2 import QtGui, QtWidgets, QtCore
import cv2
from numpy import ndarray


class ImageViewer(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = None
        self.pixel = QtGui.QPixmap()
        self.setScene(QtWidgets.QGraphicsScene(self))
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

    def render_image(
        self,
        src: ndarray,
        win_width: int = None,
        win_height: int = None,
    ):
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
        qimg = QtGui.QImage(
            self.data.data,
            w,
            h,
            self.data.ndim * w,
            QtGui.QImage.Format_RGB888,
        ).scaled(
            win_width,
            win_height,
            QtCore.Qt.KeepAspectRatio,
        )
        item = QtWidgets.QGraphicsPixmapItem(self.pixel.fromImageInPlace(qimg))
        item.setPos(0, 0)
        self.scene().clear()
        self.scene().addItem(item)
        self.scene().setSceneRect(0, 0, win_width, win_height)
        self.resize(win_width, win_height)
