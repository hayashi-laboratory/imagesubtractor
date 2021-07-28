import os

import cv2

from .contrast import Contrast


class Imagestack:
    
    def __init__(self, parent = None):
        self.windowname = "image"
        self.parent = parent
        
        
    def setdir(self, imagedir, imagenamelist):
        self.clear()
        self.imagedir = imagedir
        self.imagenamelist = imagenamelist
        self.nslice = len(self.imagenamelist)
        self.slicepos = 0
        self.cr = Contrast()
        cv2.startWindowThread()
        #WINDOW_NORMAL  need to make flexible size window
        #cv2.namedWindow(self.windowname, cv2.WINDOW_NORMAL)
        cv2.namedWindow(self.windowname, cv2.WINDOW_NORMAL+cv2.WINDOW_FREERATIO)
        self.readaimage(0)
        cv2.createTrackbar('slice',self.windowname,
                           0,self.nslice-1, self.readaimage)
        cv2.resizeWindow(self.windowname, self.image.shape[1],self.image.shape[0])
        self.cr.showhistogram(self.image)
        
    def clear(self):
        self.imagedir = None
        self.imagenamelist = list()
        self.nslice = None
        cv2.destroyAllWindows()

    # the n start from 0. not 1
    def readaimage(self, n):
        #print("read image #"+str(n))
        self.image = self[n]
        self.cr.showhistogram(self.image)
        imageshape = self.image.shape
        cv2.resizeWindow(self.windowname, imageshape[1],imageshape[0])
        #equimg = cv2.equalizeHist(self.image)
        #cv2.imshow('image',equimg)
        if self.cr.adjusted:
            newimage = self.cr.changecontrast(self.image)
            cv2.imshow(self.windowname,newimage)
        else:
            cv2.imshow(self.windowname,self.image)
        self.slicepos = n
        if self.parent is not None:
            self.parent.setroi()
        
    def __getitem__(self, n):
        #print("read image #"+str(n))
        imagepass = os.path.join(self.imagedir, self.imagenamelist[n])
        self.slicepos = n
        return cv2.imread(imagepass)

    
    def showrois(self, rois):
        passimage = self.image.copy()
        if self.cr.adjusted:
            passimage = self.cr.changecontrast(passimage)
        rois.showrois(passimage, self.windowname)
