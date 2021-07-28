# -*- coding: utf-8 -*-

"""
Created on Tue Dec  5 09:58:05 2017
Copyright (c) 2018, Taizo kawano

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################

1 Run this script
2 Click the open button and select image files directory
3 Choose a roi col x row from drop down list or manually
4 Adjust xy position and interval of roi by sliders
5 Click start and wait for about 40 min
6 Click save to save csv file in the image directory.
the csv file will be used later processing part.



Refactored on Thu Jun 17 12:43:46 2020
@author: Kuan
"""


import sys

import cv2
from PyQt5.QtWidgets import QApplication

from src.mainwindow import MainWindow


def main(args):
    try:
        app = QApplication(args)
        appUI = MainWindow()
        appUI.show()
        appUI.raise_()
        app.exec_()
    finally:
        cv2.destroyAllWindows()
        cv2.waitKey(1)


if __name__ == "__main__":
    main(sys.argv[1:])
