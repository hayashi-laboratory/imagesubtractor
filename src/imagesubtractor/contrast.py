import cv2
import numpy as np


class Contrast:
    def __init__(self):
        self.imgheight = 200
        self.imgwidth = 256
        self.min = 0
        self.max = 255
        self.winname = "contrast"
        self.image_raw = None
        self.histimage = None
        cv2.namedWindow(self.winname)
        cv2.createTrackbar("min", self.winname, 0, 255, self.setmin)
        cv2.createTrackbar("max", self.winname, 255, 255, self.setmax)

    @property
    def adjusted(self) -> bool:
        return self.min != 0 or self.max != 255

    def autocont(self, image):
        return image

    def showhistogram(self, image: np.ndarray) -> "Contrast":
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # do calc
        # tempimage = self.ic.image
        self.image_raw = image
        hist = cv2.calcHist([self.image_raw], [0], None, [256], [0, 256])
        points = self.get_points(hist)
        histimagesorce = np.zeros((self.imgheight, self.imgwidth, 3))
        cv2.fillPoly(histimagesorce, [points], (255, 255, 255))
        self.histimage = np.flipud(histimagesorce).astype(np.uint8)

        cv2.imshow(self.winname, self.histimage)

        if self.min != 0 or self.max != 255:
            self.drawaline()

        return self

    def get_points(self, hist: np.ndarray):
        verts = np.linspace(0, 1, 257).repeat(4, axis=0).reshape(257 * 2, 2)
        verts[-1, 1] = 0.0
        verts[1 : 257 * 2 - 1, 1] = hist.repeat(2) / hist.sum()
        verts[:, 0] *= self.imgwidth
        verts[:, 1] = (1 - verts[:, 1]) * self.imgheight
        return verts.round(0).astype(int)

    def update_viewimage(self):
        if isinstance(self.image_raw, np.ndarray):
            cv2.imshow("image", self.changecontrast(self.image_raw))

    def setmin(self, pos: int):
        if self.max > pos:
            self.min = pos
            self.drawaline()
            self.update_viewimage()

    def setmax(self, pos: int):
        # print("max min"+str(self.max)+" "+str(self.min)+ " v "+str(v))
        if pos > self.min:
            self.max = pos
            self.drawaline()
            self.update_viewimage()

    def drawaline(self):
        if self.histimage is not None:
            histimagewithline = self.histimage.copy()
            cv2.line(
                histimagewithline,
                (self.min, 0),
                (self.min, self.imgheight),
                (255, 0, 0),
            )
            cv2.line(
                histimagewithline,
                (self.max, 0),
                (self.max, self.imgheight),
                (0, 0, 255),
            )
            cv2.imshow(self.winname, histimagewithline)

    def calclut(self):
        # make look up table with min max
        lut = np.clip(np.arange(256, dtype=np.float64), self.min, self.max)
        lut = (lut - self.min) * 255 / (self.max - self.min)
        return lut.round(0).astype(np.uint8)

    def changecontrast(self, img):
        # use look up table
        contrastimage = cv2.LUT(img, self.calclut())
        return contrastimage
