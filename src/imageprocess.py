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
        self.roicol = getattr(self.ipg, "roicol", None)
        assert self.roicol is not None, "[ERROR] Fail to load roicollection"
        self.saveflag = saveflag
        self.threshold = threshold
        self.slicestep = slicestep
        self.normalized = normalized
        self.windowname = windowname

        cv2.startWindowThread()
        self.startslice = self.ipg.startslice
        self.endslice = self.ipg.endslice
        self.processnum = (self.endslice - self.startslice) // (self.slicestep)
        self.output = np.zeros((self.processnum, self.roicol.getlen()), dtype=np.int)
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
        # counter and cache for showing image in order
        counter: int = 0
        cache: dict = dict()
        while True:
            i, subtmedimg, binaryimg = output_queue.get()
            if i is None:
                break
            cache[i] = subtmedimg
            if self.saveflag == True:
                self.saveaimage(subtmedimg, i)
            # here must have roi processing part
            areadata = self.roicol.measureareas(binaryimg)
            self.output[i, :] = areadata

            if counter in cache:
                cv2.imshow(self.windowname, cache.pop(counter))
                cv2.setTrackbarPos("slice", self.windowname, counter)
                counter += 1

        # show remaining images
        if len(cache != 0):
            while counter in cache:
                cv2.imshow(self.windowname, cache.pop(counter))
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
