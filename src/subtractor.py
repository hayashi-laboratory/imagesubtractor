import numpy as np


class Subtractor:
    def __init__(self, normalized=False):
        self.normalized = normalized

    def setinitialimage(self, img):
        # convert from uint8 to float32
        imgf32 = img.astype(np.float32)
        if self.normalized:
            imgf32 = (imgf32 - np.mean(imgf32)) / np.std(imgf32)
        self.image1f32 = imgf32

    def set2ndimageas1st(self):
        self.image1f32 = self.image2f32

    def subtractfromholdingimage(self, img, sdrange=10):
        imgf32 = img.astype(np.float32)
        if self.normalized:
            imgf32 = (imgf32 - np.mean(imgf32)) / np.std(imgf32)
        self.image2f32 = imgf32
        return self.subtract(self.image1f32, self.image2f32, sdrange)

    def subtract(self, img1, img2, sdrange=10):
        subtimgf32 = img1 - img2
        if self.normalized:
            return self.convertfloatTo8bit(subtimgf32, -2.5, 2.5)
        else:
            mu = np.mean(subtimgf32)
            sd = np.std(subtimgf32)
            vmax = sd * sdrange
            vmin = vmax * (-1)
            return self.convertfloatTo8bit(subtimgf32 - mu, vmin, vmax)

    def convertfloatTo8bit(self, array, vmin, vmax):
        """
        Parameters
        ----------
        :array  np.ndarray: image array to be normalized
        :vmin  float: mininal value to be normalized
        :vmax  float: maximum value to be normalized
        :Returns  np.ndarray:
        ----------
        """
        # temparray = array.astype(dtype).copy()
        temparray = array.copy()
        temparray = temparray - vmin
        delta = float(vmax - vmin)
        temparray = 255 * temparray / delta
        temparray[temparray < 0] = 0
        temparray[temparray > 255] = 255
        return temparray.astype(np.uint8)
