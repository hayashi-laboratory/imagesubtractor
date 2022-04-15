
from PySide2 import QtCore, QtWidgets, QtGui


class ImageWidget(QtWidgets.QWidget):
    def __init__(self, parent= None):
        super().__init__(parent)

        


class ImageWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(0,0,500,200)
        self.title = "hello"
        self.widget, self.vbox_layout = self.init_central_widget(self)
        self.slider = self.init_slider(parent = self.widget)
        self.set_image()
        self.setCentralWidget(self.widget)

    def set_image(self):
        label = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap("/home/hayashi/Desktop/Projects/imagesubtractor/images/00000.jpg")
        label.setPixmap(pixmap)
        self.vbox_layout.addWidget(label)
        self.resize(pixmap.width(), pixmap.height()+50)
        self.slider.setFixedWidth(pixmap.width())

    def init_central_widget(self,parent):
        widget = QtWidgets.QWidget(parent = parent)
        vbox_layout = QtWidgets.QVBoxLayout(widget)
        vbox_layout.setContentsMargins(QtCore.QMargins(10, 10, 10, 10))
        widget.setLayout(vbox_layout)
        vbox_layout.setStretch(0, 1)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return widget, vbox_layout

    def init_slider(self, parent)-> QtWidgets.QSlider:
        slider = QtWidgets.QSlider(parent)
        slider.setTickInterval(1)
        slider.setSingleStep(1)
        slider.setOrientation(QtCore.Qt.Horizontal)
        
        slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        return slider


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication
    app = QApplication(sys.argv[1:])
    main = ImageWidget()
    main.show()
    main.raise_()
    sys.exit(app.exec_())