import os
import threading

import cv2
import numpy as np

from .subtractor import Subtractor
from .utils import getTime


class Imageprocess(threading.Thread):
    def __init__(
        self,
        ipg,
        saveflag=False,
        threshold=2,
        slicestep=1,
        windowname="subtmed",
        **kwargs,
    ):
        super().__init__(daemon=True)
        self.ipg = ipg
        self.imagestack = getattr(self.ipg, "ims", None)
        assert self.imagestack is not None, ""
        self.saveflag = saveflag
        self.threshold = threshold
        self.slicestep = slicestep
        self.windowname = windowname

        cv2.startWindowThread()
        cv2.namedWindow(self.windowname, cv2.WINDOW_NORMAL)
        self.startslice = self.ipg.startslice
        self.endtslice = self.ipg.endslice
        self.processnum = (self.endtslice - self.startslice) // (self.slicestep)
        self.output = np.zeros(
            (self.processnum, self.ipg.roicol.getlen()), dtype=np.int
        )
        self.image1 = self.imagestack[self.startslice]

    def nothing(self, n):
        pass

    def batch(img1, img2, subtractor):
        pass

    def run(self):
        start = getTime()
        print(f"[SYSTEM] Start at: {start}")
        subtractor = Subtractor()
        subtractor.setinitialimage(self.image1)

        for i in range(self.processnum):
            currentslice = int(self.startslice + i * self.slicestep)
            nextimg = self.imagestack[currentslice + int(1 * self.slicestep)]
            subimage = subtractor.subtractfromholdingimage(nextimg)
            subtractor.set2ndimageas1st()
            # on imagej macro run("Median...", "radius=2");
            # it may coresspond with 3? no. it seems imagejs radian =1
            # so need 6?odd5 or rgb 9?
            # 5 seems closer to imagej radian=2. looks differennt algorism.
            # so may not able to give same result.
            subtmedimg = cv2.medianBlur(subimage, 5)
            # subimage = self.subtract(currentslice,currentslice+1)
            if self.saveflag == True:
                self.saveaimage(subtmedimg, i)
            cv2.imshow(self.windowname, subtmedimg)

            cv2.setTrackbarPos("slice", self.windowname, i)

            # 3sd 127-3*12.7
            threshold = 127 - self.threshold * 12.8
            retval, binaryimg = cv2.threshold(
                subtmedimg, threshold, 1, cv2.THRESH_BINARY_INV
            )

            # here must have roi processing part
            areadata = self.ipg.roicol.measureareas(binaryimg)
            self.output[i, :] = areadata
        end = getTime()
        self.ipg.outputdata = self.output
        self.ipg.savedata()

    def saveaimage(self, img, num):
        # filename="".join([datetime.datetime.now().strftime('%Y%m%d%H%M%S_%f'),'.jpg'])
        # filename="".join([str(num),'.jpg'])
        filename = "%d.tif" % num
        # tif format saving seems not work in this way. need fix. it is saved as binary (black/white)image?
        # quality 80? 95? imagej default seems 85
        filepath = os.path.join(self.ipg.imagedir, filename)
        """
        cv2.imwrite(filepass, img,
                    [int(cv2.IMWRITE_JPEG_QUALITY),85])
        """
        cv2.imwrite(filepath, img)
        print("saved in", filepath)
