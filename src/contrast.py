import cv2
import numpy as np


class Contrast:
    def __init__(self):
        self.imgheight = 200
        self.imgwidth = 256
        self.min = 0
        self.max = 255
        self.adjusted = False
        self.windowname = "contrast"
        cv2.namedWindow(self.windowname)
        cv2.createTrackbar("min", self.windowname, 0, 255, self.setmin)
        cv2.createTrackbar("max", self.windowname, 255, 255, self.setmax)

    def autocont(self, image):
        return image

    def showhistogram(self, image):
        # font = cv2.FONT_HERSHEY_SIMPLEX
        # do calc
        # tempimage = self.ic.image
        self.tempimage = image
        hist = cv2.calcHist([self.tempimage], [0], None, [256], [0, 256])
        histimagesorce = np.zeros((self.imgheight, self.imgwidth, 3))
        for i, val in enumerate(hist):
            # value must be adjusted by image size (pixel num)
            # and max value of hist?
            cv2.line(histimagesorce, (i, 0), (i, int(val / 100)), (255, 255, 255))
        self.histimage = np.flipud(histimagesorce)
        """cv2.putText(histimage, str(i+1)+"/"+str(self.maxframe), 
                            (50,50), font, 1, 255,2)
        """
        # this line is just work around for the opencv bug?
        # https://stackoverflow.com/questions/30249053/python-opencv-drawing-errors-after-manipulating-array-with-numpy
        """
        histimage = histimage.copy()
        cv2.putText(histimage, "median "+str(np.median(tempimage)),
                     (10,12), font, 0.5, (255,255,255),
                     1, cv2.LINE_AA)
        """
        cv2.imshow(self.windowname, self.histimage)

        if self.min != 0 or self.max != 255:
            self.drawaline()

    def show_image(self):
        tempimage = getattr(self, "tempimage", None)
        if isinstance(tempimage, np.ndarray):
            cv2.imshow("image", self.changecontrast(tempimage))

    def setmin(self, v):
        self.adjusted = True
        # print("max min"+str(self.max)+" "+str(self.min)+ " v "+str(v))
        if self.max > v:
            self.min = v
            self.drawaline()
            self.show_image()

    def setmax(self, v):
        self.adjusted = True
        # print("max min"+str(self.max)+" "+str(self.min)+ " v "+str(v))
        if v > self.min:
            self.max = v
            self.drawaline()
            self.show_image()

    def drawaline(self):
        histimage = getattr(self, "histimage", None)
        if isinstance(histimage, np.ndarray):
            histimagewithline = histimage.copy()
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
            cv2.imshow(self.windowname, histimagewithline)

    def calclut(self):
        # make look up table with min max
        lut = np.clip(np.arange(256), self.min, self.max)
        lut = (lut - self.min) * 255 / (self.max - self.min)
        return lut.astype(np.uint8)

    def changecontrast(self, img):
        # use look up table
        contrastimage = cv2.LUT(img, self.calclut())
        return contrastimage
