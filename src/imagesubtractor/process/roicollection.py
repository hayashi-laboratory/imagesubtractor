import functools
from collections import UserList
from typing import Dict, List, Optional

import numpy as np

from ..utils import load_json
from .roi import Roi

__all__ = ["RoiCollection"]


class RoiCollection(UserList):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.data: List[Roi]

    @property
    def roidict(self) -> Dict[str, Dict]:
        return dict(
            rois={int(roi.order): roi.to_dict() for roi in self.data},
            roisarg=getattr(self, "roisarg", {}),
        )

    def set_roisarg(self, roisarg: Dict[str, Dict]) -> "RoiCollection":
        self.roisarg = roisarg or dict()
        return self

    def set_rois(
        self,
        roicolnum: int,
        roirownum: int,
        roiintervalx: int,
        roiintervaly: int,
        x: int,
        y: int,
        box_width: int,
        box_height: int,
        radianrot: int,
        xmax: Optional[int] = None,
        ymax: Optional[int] = None,
    ) -> "RoiCollection":
        int_max = np.iinfo(int).max
        ymax, xmax = int_max, int_max
        self.roisarg = {
            "roicolnum": roicolnum,
            "roirownum": roirownum,
            "roiintervalx": roiintervalx,
            "roiintervaly": roiintervaly,
            "x": x,
            "y": y,
            "width": box_width,
            "height": box_height,
            "radianrot": radianrot,
        }

        if isinstance(xmax, int):
            xmax -= box_width
        if isinstance(ymax, int):
            ymax -= box_height

        xy_shift = np.expand_dims(np.array((x, y)), 1)
        rot_cos, rot_sin = np.cos(radianrot), np.sin(radianrot)

        rotation_matrix = np.array([(rot_cos, -rot_sin), (rot_sin, rot_cos)])
        x_cols = np.arange(roicolnum) * roiintervalx
        y_rows = np.arange(roirownum) * roiintervaly
        grid = np.asarray(np.meshgrid(x_cols, y_rows)).reshape(2, -1)

        pos = rotation_matrix.dot(grid) + xy_shift
        pos[0] = np.clip(pos[0], 0, xmax)
        pos[1] = np.clip(pos[1], 0, ymax)

        pos = pos.astype(int).T
        self.clear()
        self.extend(
            (
                Roi(xpos, ypos, box_width, box_height, i)
                for i, (xpos, ypos) in enumerate(pos)
            )
        )
        return self

    def draw_rois(self, image: np.ndarray) -> np.ndarray:
        return functools.reduce(self.draw_a_roi, self.data, image)

    def draw_a_roi(self, image: np.ndarray, roi: Roi) -> np.ndarray:
        return roi.show(image)

    def measureareas(self, img: np.ndarray) -> np.ndarray:
        return np.fromiter((roi.measurearea(img) for roi in self.data), int)

    @classmethod
    def from_json(cls, path: str) -> "RoiCollection":
        params_dict = load_json(path)
        if "rois" in params_dict:
            rois_dict = params_dict.get("rois")
        elif any(lambda num: num in params_dict, range(48)) or len(params_dict) == 48:
            rois_dict = params_dict
        rois = (Roi(**kws) for kws in rois_dict.values())
        return cls(sorted(rois, key=lambda x: x.order)).set_roisarg(
            params_dict.get("roisarg")
        )
