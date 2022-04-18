from numpy import ndarray
from PySide2 import QtCore, QtWidgets

from .imageviewer import ImageViewer
from .sliderwithvalue import SliderWithValue


class SliderViewer(QtWidgets.QWidget):
    def __init__(self, parent=None, processnum: int = 1000):
        super().__init__(parent=parent)
        self.setWindowTitle("Processing...")
        layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(layout)
        self.slider = SliderWithValue(self)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.setMaximum(processnum)

        self.progress = QtWidgets.QProgressBar(parent)
        self.setRange = self.progress.setRange
        self.setValue = self.progress.setValue
        self.valueChanged = self.slider.valueChanged

        self.canvas = ImageViewer(self)
        layout.addWidget(self.slider)
        layout.addWidget(self.canvas)
        layout.addWidget(self.progress)
        self.show()

    def setMaximum(self, max_val: int):
        self.slider.setMaximum(max_val)

    @property
    def value(self) -> int:
        return self.slider.value()

    def imshow(self, image: ndarray, pos: int = None):
        if isinstance(pos, int):
            self.slider.setValue(pos)
        self.canvas.render_image(image, self.width(), self.height())
