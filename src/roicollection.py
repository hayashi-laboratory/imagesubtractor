
import functools

import cv2
import numpy as np

from .roi import Roi
from .utils import load_json

##################################################################
class Roicollection:
    #upperobj could be imageprocessgui, imagecapturegui?
    def __init__(self, parent):
        self.upperobj = parent
        self.roilist = []
        self.roidict = dict()
        self.paramdict = dict()
    
    def __iter__(self):
        return iter(self.roilist)
        
    def __len__(self):
        return len(self.roilist)

    def __getitem__(self, index):
        return self.roilist[index]
    
    def getlen(self):
        return len(self)
    """
    roisarg = [roicolnum, roirownum, roiintervalx, roiintervaly,
               x, y, width, height, radianrot]
    self.roilist.setrois(**roisarg)
    """
    def setrois(self, roicolnum, roirownum, roiintervalx, roiintervaly,
                x, y, width, height, radianrot):
        int_max = np.iinfo(int).max
        ymax, xmax = int_max, int_max
        roisarg = {"roicolnum":roicolnum,
                    "roirownum": roirownum,
                    "roiintervalx":roiintervalx,
                    "roiintervaly":roiintervaly,
                    "x":x,
                    "y":y,
                    "width":width,
                    "height":height,
                    "radianrot":radianrot}
        if self.upperobj.ims is not None:
            ymax, xmax = self.upperobj.ims[0].shape[:2]
                
        xy_shift = np.expand_dims(np.array((x,y)), 1)
        rot_cos, rot_sin = np.cos(radianrot), np.sin(radianrot)
        
        rotation_matrix = np.array([(rot_cos, -rot_sin),
                               (rot_sin, rot_cos)])
        x_cols = np.arange(roicolnum) * roiintervalx
        y_rows = np.arange(roirownum) * roiintervaly
        grid = np.asarray(np.meshgrid(x_cols,y_rows)).reshape(2,-1)
        
        pos = rotation_matrix.dot(grid) + xy_shift
        pos[0] = np.clip(pos[0], 0, xmax - width)
        pos[1] = np.clip(pos[1], 0, ymax - height)

        pos = pos.astype(int).T
 
        self.roilist = [Roi(self.upperobj, xpos, ypos, width, height, i)
                        for i, (xpos,ypos) in enumerate(pos)]
        self.roidict["rois"] = {int(roi.order):roi.to_dict() for roi in self.roilist}
        self.roidict["roisarg"] = roisarg
                #print("pos "+str(int(x+shiftx))+" "+str(int(y+shifty)))
        
    def append(self, roi):
        self.roilist.append(roi)

    
    def showrois(self, baseimage, windowname):
        #slicepos = self.ims.slicepos
        if len(self.roilist) > 0:
            #def show(self, slicepos):
            #baseimage = self.ims.getaimage(slicepos)
            modimage = functools.reduce(lambda img, roi: roi.show(img), self, baseimage)
            cv2.imshow(windowname, modimage)
    
    #the img must be binary. 0 or 1
    def measureareas(self, img):
        return np.fromiter((roi.measurearea(img) for roi in self), int)
    
    def read_json(self, path):
        self.roidict = load_json(path)
        roidicts = self.roidict if len(self.roidict) == 48 else self.roidict.get("rois")
        if isinstance(roidicts, dict):
            self.roilist = [Roi(self.upperobj, **value) for value in roidicts.values()]
