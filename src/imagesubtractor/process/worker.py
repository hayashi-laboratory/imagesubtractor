import multiprocessing as mp
import os
from pathlib import Path

import cv2

from .queue_item import Result
from .roicollection import RoiCollection
from .subtractor import Subtractor

__all__ = ["SubtractorWorker"]


class SubtractorWorker(mp.Process):
    def __init__(
        self,
        task: mp.Queue,
        output: mp.Queue,
        roicollection: RoiCollection,
        subtractor: Subtractor,
        saveflag: bool = False,
    ):
        super().__init__(daemon=True)
        self.task = task
        self.output = output
        self.roicol = roicollection
        self.subtractor = subtractor
        self.saveflag = saveflag

    def run(self):
        while not self.task.empty():
            num, p1, p2 = self.task.get()
            if num is None:
                break
            subtract, blur, binary = (
                self.subtractor.set_image(cv2.imread(p1), 0)  # img1
                .set_image(cv2.imread(p2), 1)  # img2
                .subtract()  # img2 -img1 -> subtract
                .median_blur(ksize=5)  # subtract -> blur
                .threshold_binarize()  # blur -> binary
                .get_results()  # retrieve subtract, blur, binary
            )
            if self.saveflag:
                filepath = Path(p1).parent.joinpath(f"{num:0>6}_sub.tif")
                cv2.imwrite(os.fspath(filepath), blur)
                print("saved in", filepath)

            areadata = self.roicol.measureareas(binary)
            self.output.put(Result(num, subtract, areadata))
