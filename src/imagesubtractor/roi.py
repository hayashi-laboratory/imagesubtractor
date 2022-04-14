from dataclasses import dataclass, field
from typing import OrderedDict

import cv2
import numpy as np


@dataclass(frozen=True, order=True)
class Roi:
    x: int = field(compare=False)
    y: int = field(compare=False)
    width: int = field(compare=False)
    height: int = field(compare=False)
    order: int = field(compare=True)

    # def show(self, slicepos):
    def show(self, image: np.ndarray) -> np.ndarray:
        modimage = image
        # 0,255,255 yellow
        FONT = cv2.FONT_HERSHEY_SIMPLEX
        YELLOW = (0, 255, 255)
        cv2.putText(
            img=modimage,
            text=str(self.order),
            org=(self.x, max(0, self.y - 5)),
            fontFace=FONT,
            fontScale=0.5,
            color=YELLOW,
            thickness=1,
            lineType=cv2.LINE_AA,
        )
        cv2.rectangle(
            img=modimage,
            pt1=(self.x, self.y),
            pt2=(self.x + self.width, self.y + self.height),
            color=YELLOW,
            thickness=2,
        )
        return modimage

    # the img must be binary. 0 or 1
    def measurearea(self, img: np.ndarray) -> int:
        roiimg = img[
            self.y : self.y + self.height + 1, self.x : self.x + self.width + 1
        ]
        value = roiimg.sum()
        if roiimg.ndim == 3:
            y, x, dim = roiimg.shape
            value = value // dim
        return value

    def to_dict(self) -> OrderedDict:
        return OrderedDict(
            [
                ("x", int(self.x)),
                ("y", int(self.y)),
                ("width", self.width),
                ("height", self.height),
                ("order", self.order),
            ]
        )

    def copy(self) -> "Roi":
        return type(self)(**self.to_dict())
