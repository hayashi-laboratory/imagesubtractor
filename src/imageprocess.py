import os
import threading
from multiprocessing import Queue

import cv2
import numpy as np

from .parallel_subtractor import ParallelSubtractor
from .utils import getTime


class Imageprocess(threading.Thread):
    def __init__(
        self,
        ipg,
        saveflag=False,
        threshold=2,
        slicestep=1,
        normalized=False,
        windowname="subtmed",
        **kwargs,
    ):
        super().__init__(daemon=True)
        self.ipg = ipg
        self.imagestack = getattr(self.ipg, "ims", None)
        assert self.imagestack is not None, "[ERROR] Fail to load imagestack"
        self.saveflag = saveflag
        self.threshold = threshold
        self.slicestep = slicestep
        self.normalized = normalized
        self.windowname = windowname

        cv2.startWindowThread()
        self.startslice = self.ipg.startslice
        self.endslice = self.ipg.endslice
        self.processnum = (self.endslice - self.startslice) // (self.slicestep)
        self.output = np.zeros(
            (self.processnum, self.ipg.roicol.getlen()), dtype=np.int
        )
        self.image1 = self.imagestack[self.startslice]

    def nothing(self, n):
        pass

    def run(self):
        print(f"[SYSTEM] Start at: {getTime()}")
        output_queue = Queue()
        subtractors = ParallelSubtractor(
            self.startslice,
            self.endslice,
            self.slicestep,
            self.imagestack,
            output_queue,
            self.normalized,
            daemon=True,
        )
        subtractors.start()
        # namedWindow after processing
        cv2.namedWindow(self.windowname, cv2.WINDOW_NORMAL)
        # this is for opencv imshow
        counter = 0
        tempdict = dict()
        while True:
            i, subtmedimg, binaryimg = output_queue.get()
            tempdict[i] = subtmedimg
            if i is None:
                break
            if self.saveflag == True:
                self.saveaimage(subtmedimg, i)
            # here must have roi processing part
            areadata = self.ipg.roicol.measureareas(binaryimg)
            self.output[i, :] = areadata

            if counter in tempdict:
                cv2.imshow(self.windowname, tempdict.pop(counter))
                cv2.setTrackbarPos("slice", self.windowname, counter)
                counter += 1

        # imshow remain images
        while counter in tempdict:
            cv2.imshow(self.windowname, tempdict.pop(counter))
            cv2.setTrackbarPos("slice", self.windowname, counter)
            counter += 1

        self.ipg.outputdata = self.output
        self.ipg.savedata()
        print(f"[SYSTEM] End at: {getTime()}")

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
