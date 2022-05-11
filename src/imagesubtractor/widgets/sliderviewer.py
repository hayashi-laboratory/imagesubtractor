from numpy import ndarray
from PySide2 import QtCore, QtWidgets

from .imageviewer import ImageViewer


class SliderViewer(QtWidgets.QWidget):
    def __init__(self, parent=None, processnum: int = 1000):
        super().__init__(parent=parent)
        self.setWindowTitle("Processing...")
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.slider = QtWidgets.QSlider(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(1)
        self.slider.setMaximum(processnum)

        self.valueChanged = self.slider.valueChanged

        self.canvas = ImageViewer(self)
        layout.addWidget(self.slider)
        layout.addWidget(self.canvas)
        self.show()

    def setMaximum(self, max_val: int):
        self.slider.setMaximum(max_val)

    def setStep(self, step: int):
        self.slider.setSingleStep(max(step, 1))
        self.slider.setPageStep(max(step, 1))

    @property
    def value(self) -> int:
        return self.slider.value()

    def imshow(self, image: ndarray, pos: int = None):
        if isinstance(pos, int):
            self.slider.setValue(pos)
        self.canvas.render_image(
            image, int(self.width() * 0.95), int(self.height() * 0.95)
        )

    def setDisabled(self, disable: bool) -> None:
        self.slider.setDisabled(disable)
