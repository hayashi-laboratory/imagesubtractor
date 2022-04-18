from PySide2 import QtCore, QtGui, QtWidgets


class SliderWithValue(QtWidgets.QSlider):
    def __init__(self, parent=None):
        super(SliderWithValue, self).__init__(parent)

        self.stylesheet = """
        QSlider::groove:vertical {
                background-color: #222;
                width: 30px;
        }
        QSlider::handle:vertical {
            border: 1px #438f99;
            border-style: outset;
            margin: -2px 0;
            width: 30px;
            height: 3px;
            background-color: #438f99;
        }
        QSlider::sub-page:vertical {
            background: #4B4B4B;
        }
        QSlider::groove:horizontal {
                background-color: #222;
                height: 30px;
        }
        QSlider::handle:horizontal {
            border: 1px #438f99;
            border-style: outset;
            margin: -2px 0;
            width: 3px;
            height: 30px;
            background-color: #438f99;
        }
        QSlider::sub-page:horizontal {
            background: #4B4B4B;
        }
        """

        # self.setStyleSheet(self.stylesheet)

    def paintEvent(self, event):
        QtWidgets.QSlider.paintEvent(self, event)

        round_value = str(int(self.value()))

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.black))

        font_metrics = QtGui.QFontMetrics(self.font())
        font_width = font_metrics.boundingRect(str(round_value)).width()
        font_height = font_metrics.boundingRect(str(round_value)).height()

        rect = self.geometry()
        if self.orientation() not in (QtCore.Qt.Horizontal, QtCore.Qt.Vertical):
            painter.drawRect(rect)
            return

        if self.orientation() == QtCore.Qt.Horizontal:
            horizontal_x_pos = rect.width() - font_width - 5
            horizontal_y_pos = rect.height() * 0.75
            pt = QtCore.QPoint(horizontal_x_pos, horizontal_y_pos)

        else:
            vertical_x_pos = rect.width() - font_width - 5
            vertical_y_pos = rect.height() * 0.75
            pt = QtCore.QPoint(rect.width() / 2.0 - font_width / 2.0, rect.height() - 5)

        painter.drawText(pt, round_value)
        painter.drawRect(rect)
