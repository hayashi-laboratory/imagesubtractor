from dataclasses import dataclass, field

import cv2


@dataclass(frozen=True, order=True)
class Roi:
    ipg: type = field(repr=False, hash=False)
    x: int = field(compare=False)
    y: int = field(compare=False)
    width: int = field(compare=False)
    height: int = field(compare=False)
    order: int = field(compare=True)

    # def show(self, slicepos):
    def show(self, image):
        modimage = image
        # 0,255,255 yellow
        FONT = cv2.FONT_HERSHEY_SIMPLEX
        YELLOW = (0, 255, 255)
        cv2.putText(
            modimage,
            str(self.order),
            (self.x, max(0, self.y - 5)),
            FONT,
            0.5,
            YELLOW,
            1,
            cv2.LINE_AA,
        )
        cv2.rectangle(
            modimage,
            (self.x, self.y),
            (self.x + self.width, self.y + self.height),
            YELLOW,
            2,
        )
        return modimage
        # cv2.imshow("image", modimage)

    # the img must be binary. 0 or 1
    def measurearea(self, img):
        roiimg = img[
            self.y : self.y + self.height + 1, self.x : self.x + self.width + 1
        ]
        value = roiimg.sum()
        if roiimg.ndim == 3:
            y, x, dim = roiimg.shape
            value = value // dim
        return value

    def to_dict(self):
        return {
            "x": int(self.x),
            "y": int(self.y),
            "width": self.width,
            "height": self.height,
            "order": self.order,
        }
