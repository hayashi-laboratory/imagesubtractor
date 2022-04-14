import multiprocessing as mp
import os
import threading
from typing import Dict, Tuple

import cv2
import numpy as np

from .imagestack import Imagestack
from .parallel_subtractor import ParallelSubtractor
from .roicollection import RoiCollection
from .utils import get_time


class Imageprocess(threading.Thread):
    def __init__(
        self,
        winname="subtmed",
    ):
        super().__init__(daemon=True)
        self.winname = winname
        cv2.startWindowThread()

    def nothing(self, n):
        pass

    def setup_parallel_subtractor(self, subtractor:ParallelSubtractor, outputdata:np.ndarray) ->"Imageprocess":
        self.output = outputdata
        self.subtractors = subtractor
        return self

    def run(self):
        print(f"[SYSTEM] Start at: {get_time()}")
        self.subtractors.start()
        cv2.namedWindow(self.winname, cv2.WINDOW_NORMAL)
        # counter and cache for showing image in order
        counter: int = 0
        cache:Dict[int, np.ndarray] = dict()

        while not self.subtractors.empty():
            i, subtmedimg, areadata = self.subtractors.retrieve()
            if (i is None):
                break
            self.output[i, :] = areadata
            cache[i] = subtmedimg
            if counter in cache:
                cv2.imshow(self.winname, cache.pop(counter))
                cv2.setTrackbarPos("slice", self.winname, counter)
                counter += 1
        
        # show remaining images
        if len(cache) != 0:
            while counter in cache:
                cv2.imshow(self.winname, cache.pop(counter))
                cv2.setTrackbarPos("slice", self.winname, counter)
                counter += 1

        print(f"[SYSTEM] End at: {get_time()}")

