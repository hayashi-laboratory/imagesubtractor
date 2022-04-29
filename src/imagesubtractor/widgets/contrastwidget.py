from typing import Tuple
from numpy import ndarray
from PySide2 import QtCore, QtGui, QtWidgets

from .imageviewer import ImageViewer


class ContrastWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.resize(270, 200)

        self.low = QtWidgets.QSpinBox(self)
        self.low.setAlignment(QtCore.Qt.AlignRight)
        self.low.setFixedWidth(50)
        self.low.setSingleStep(1)
        self.low.setMinimum(0)
        self.low.setMaximum(255)
        self.low.setValue(0)

        self.high = QtWidgets.QSpinBox(self)
        self.high.setAlignment(QtCore.Qt.AlignRight)
        self.high.setFixedWidth(50)
        self.high.setSingleStep(1)
        self.high.setMinimum(0)
        self.high.setMaximum(255)
        self.high.setValue(255)

        self.reset_btn = QtWidgets.QPushButton("Reset", self)
        self.reset_btn.setFixedWidth(50)
        self.reset_btn.clicked.connect(self.reset_value)
        self.reset_btn.setFont(self.__get_font())

        self.canvas = ImageViewer(self)
        self.canvas.resize(250, 180)

        self.low_label = self.set_label("low", self.low)
        self.high_label = self.set_label("high", self.high)
        self.view_label = self.set_label("Histogram", self.canvas)

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.view_label, 0, 1, 1, 23, QtCore.Qt.AlignCenter)
        layout.addWidget(self.low_label, 0, 0, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.low, 1, 0, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.high_label, 2, 0, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.high, 3, 0, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.reset_btn, 4, 0, 1, 1, QtCore.Qt.AlignCenter)
        layout.addWidget(self.canvas, 1, 1, 5, 24)

        self.low.valueChanged.connect(self.spinbox_callback)
        self.high.valueChanged.connect(self.spinbox_callback)

        self.update_canvas = None

    def __get_font(self):
        font = QtGui.QFont("helvetica")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        return font

    def set_label(
        self,
        label_text: str = "",
        buddy: QtWidgets.QWidget = None,
    ) -> QtWidgets.QLabel:
        font = self.__get_font()
        label = QtWidgets.QLabel(text=label_text, parent=self)
        if buddy is not None:
            label.setBuddy(buddy)
        label.setFont(font)
        return label

    def spinbox_callback(self):
        self.high.setMinimum(self.low.value() + 1)
        self.low.setMaximum(self.high.value() - 1)
        if callable(self.update_canvas):
            self.update_canvas()

    def imshow(self, image: ndarray):
        self.canvas.render_image(
            image,
            self.canvas.width(),
            self.canvas.height(),
            False,
        )
        self.update()

    def get_range(self) -> Tuple[int, int]:
        return self.low.value(), self.high.value()

    def reset_value(self):
        self.low.setValue(0)
        self.high.setValue(255)

    def setDisabled(self, disable: bool) -> None:
        self.low.setDisabled(disable)
        self.high.setDisabled(disable)
        self.reset_btn.setDisabled(disable)
