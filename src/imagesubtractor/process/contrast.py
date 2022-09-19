import cv2
import numpy as np


class Contrast:
    def __init__(self):
        self.imgheight = 180
        self.imgwidth = 384
        self.min = 0
        self.max = 255

    def set_range(self, min_=0, max_=255) -> "Contrast":
        if isinstance(min_, int):
            self.min = min_
        if isinstance(max_, int):
            self.max = max_
        return self

    @property
    def adjusted(self) -> bool:
        return self.min != 0 or self.max != 255

    def draw_histogram(self, image: np.ndarray) -> np.ndarray:
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # do calc
        # tempimage = self.ic.image
        image = image
        hist = cv2.calcHist([image], [0], None, [256], [0, 256])
        points = self.get_points(hist)
        histimagesorce = np.zeros((self.imgheight, self.imgwidth, 3), dtype=np.uint8)
        cv2.fillPoly(histimagesorce, [points], (255, 204, 153))
        histimage = np.fliplr(histimagesorce).astype(np.uint8)

        if self.adjusted:
            histimage = self.drawaline(histimage)

        return histimage

    def get_points(self, hist: np.ndarray):
        verts = np.linspace(0, 1, 257).repeat(4, axis=0).reshape(257 * 2, 2)
        verts[-1, 1] = 0.0
        verts[1 : 257 * 2 - 1, 1] = hist.repeat(2) / hist.max()
        verts[:, 0] *= self.imgwidth
        verts[:, 1] = (1 - verts[:, 1]) * self.imgheight
        return verts.round(0).astype(int)

    def drawaline(self, image: np.ndarray):
        min_ = round(self.min / 255.0 * self.imgwidth)
        max_ = round(self.max / 255.0 * self.imgwidth)

        mask = np.zeros_like(image, np.uint8)
        mask[:, :min_] = (222, 0, 0)
        mask[:, max_:] = (0, 0, 222)
        cv2.line(
            image,
            (min_, 0),
            (min_, self.imgheight),
            (255, 0, 0),
            1,
            cv2.LINE_AA,
        )
        cv2.line(
            image,
            (max_, 0),
            (max_, self.imgheight),
            (0, 0, 255),
            1,
            cv2.LINE_AA,
        )
        cv2.line(
            image,
            (min_, self.imgheight),
            (max_, 0),
            (255, 255, 255),
            1,
            cv2.LINE_AA,
        )
        return cv2.addWeighted(image, 1.0, mask, 0.75, 1.0)

    def calclut(self) -> np.ndarray:
        # make look up table with min max
        lut = np.clip(np.arange(256, dtype=np.float64), self.min, self.max)
        lut = (lut - self.min) * 255 / (self.max - self.min)
        return lut.round(0).astype(np.uint8)

    def draw_contrast(self, img: np.ndarray) -> np.ndarray:
        # use look up table
        return cv2.LUT(img, self.calclut())
