from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import cv2
import numpy as np

__all__ = ["Subtractor"]


@dataclass
class Subtractor:
    threshold: float
    normalized: bool = False
    data: Dict[str, np.ndarray] = field(init=False, repr=False, default_factory=dict)

    def set_image(self, img: np.ndarray, position: int) -> "Subtractor":
        if position not in (0, 1, "0", "1"):
            raise ValueError(
                "Only position 0(first) or 1(second) can be set for subtractor"
            )
        imgf32 = img.astype(np.float32)
        if self.normalized:
            imgf32 = (imgf32 - np.mean(imgf32)) / np.std(imgf32)
        self.data[str(position)] = imgf32
        return self

    def remove_results(self):
        self.data.pop("subtract", None)
        self.data.pop("blur", None)
        self.data.pop("binary", None)

    def subtract(self, sdrange=10) -> "Subtractor":
        self.remove_results()
        im1, im2 = self.data.get("0"), self.data.get("1")
        if not isinstance(im1, np.ndarray) or not isinstance(im2, np.ndarray):
            raise TypeError(f"images are not properly set. {(im1, im2)}")

        subtimgf32 = im2 - im1
        if self.normalized:
            sub_img = self.convertfloatTo8bit(subtimgf32, -2.5, 2.5)
        else:
            mu = np.mean(subtimgf32)
            sd = np.std(subtimgf32)
            vmax = sd * sdrange
            vmin = vmax * (-1)
            sub_img = self.convertfloatTo8bit(subtimgf32 - mu, vmin, vmax)
        self.data["subtract"] = sub_img
        return self

    def median_blur(self, ksize=5) -> "Subtractor":
        sub_img = self.data.get("subtract", None)
        if sub_img is None:
            raise ValueError("Subtractor.subtract must be run before medianBlur")
        self.data["blur"] = cv2.medianBlur(sub_img, ksize)
        return self

    def threshold_binarize(self) -> "Subtractor":
        blur = self.data.get("blur", None)
        if blur is None:
            raise ValueError("Subtractor.subtract must be run before median_blur")

        threshold = max(127 - self.threshold * 12.8, 0)
        _, binary = cv2.threshold(
            blur,
            threshold,
            1,
            cv2.THRESH_BINARY_INV,
        )
        self.data["binary"] = binary

        return self

    def get_results(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """retrieve the results

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: subtract, blur, binary
        """
        return self.data.get("subtract"), self.data.get("blur"), self.data.get("binary")

    @classmethod
    def convertfloatTo8bit(cls, array: np.ndarray, vmin: int, vmax: int) -> np.ndarray:
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
