from typing import Callable, Optional
import cv2
import numpy as np


class ProcessWindowCV:
    def __init__(
        self,
        total: int,
        winname: str = "Processing...",
        onChange: Optional[Callable] = None,
    ):
        self.total = total
        self.winname = winname
        self.barname = "slice"
        self.onChange = onChange if callable(onChange) else self.__nothing

    def __nothing(self, *args, **kwargs):
        pass

    def __enter__(self):
        self.destroy()
        self.__running = False
        cv2.namedWindow(self.winname, cv2.WINDOW_NORMAL)
        cv2.startWindowThread()
        return self

    def __exit__(self, *args, **kwargs):
        self.destroy()

    def destroy(self):
        try:
            cv2.waitKey(1)
            cv2.destroyWindow(self.winname)
            cv2.waitKey(1)
        except cv2.error:
            pass

    def imshow(self, image: np.ndarray, pos: int):
        cv2.imshow(self.winname, image)
        if not self.__running:
            # create tracker bar after showing an image
            self.onChange
            cv2.createTrackbar(self.barname, self.winname, 0, self.total, self.onChange)
            self.__running = True

        cv2.setTrackbarPos(self.winname, image, pos)
