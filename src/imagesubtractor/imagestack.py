import multiprocessing as mp
import os
import os.path as osp
from typing import List

import cv2
import numpy as np

from .contrast import Contrast


class Imagestack:
    def __init__(self):
        self.winname = "image"

    def setdir(self, imagedir: str, imagenamelist: List[str]) -> "Imagestack":
        self.imagedir = imagedir
        self.imagenamelist = imagenamelist
        self.nslice = len(self.imagenamelist)
        self.slicepos = 0
        # WINDOW_NORMAL  need to make flexible size window
        # cv2.namedWindow(self.windowname, cv2.WINDOW_NORMAL)
        cv2.namedWindow(self.winname, cv2.WINDOW_NORMAL + cv2.WINDOW_FREERATIO)
        self.cr = Contrast()
        self.readaimage(0)
        cv2.createTrackbar("slice", self.winname, 0, self.nslice - 1, self.readaimage)
        return self


    # the n start from 0. not 1
    def readaimage(self, n):
        # print("read image #"+str(n))
        self.image = self[n]
        self.cr.showhistogram(self.image)
        height, width = self.image.shape[:2]
        cv2.resizeWindow(self.winname, width, height)
        # equimg = cv2.equalizeHist(self.image)
        # cv2.imshow('image',equimg)
        if self.cr.adjusted:
            newimage = self.cr.changecontrast(self.image)
            cv2.imshow(self.winname, newimage)
        else:
            cv2.imshow(self.winname, self.image)
        self.slicepos = n

    def __getitem__(self, n) -> np.ndarray:
        # print("read image #"+str(n))
        imagepass = os.path.join(self.imagedir, self.imagenamelist[n])
        return cv2.imread(imagepass)

    def showrois(self, rois):
        passimage = self.image.copy()
        if self.cr.adjusted:
            passimage = self.cr.changecontrast(passimage)
        rois.showrois(passimage, self.winname)

    def get_image_queue(
        self,
        start: int,
        end: int,
        slicestep: int,
    ):
        queue = mp.Queue()
        imagedir = self.imagedir
        imagenamelist = self.imagenamelist
        step_num = range(start, end + 1, slicestep)
        for i, (pos1, pos2) in enumerate(zip(step_num[:-1], step_num[1:])):
            queue.put_nowait(
                (
                    i,
                    osp.join(imagedir, imagenamelist[pos1]),
                    osp.join(imagedir, imagenamelist[pos2]),
                )
            )
        queue.put_nowait((None, None, None))
        return queue
