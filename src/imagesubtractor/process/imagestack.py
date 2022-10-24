import multiprocessing as mp
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple, Union

import cv2
from numpy import ndarray

from .queue_item import Task

__all__ = ["Imagestack"]


@dataclass
class Imagestack:
    homedir: Path = field(init=False, default=Path("."))
    imagelist: List[Path] = field(init=False, default_factory=list)
    img_width: Optional[int] = field(init=False, default=None)
    img_height: Optional[int] = field(init=False, default=None)

    def __len__(self):
        return self.imagelist.__len__()

    def set_folder(self, homedir: Union[str, Path]) -> "Imagestack":
        self.homedir = Path(homedir)
        self.imagelist = sorted(
            [
                f
                for f in self.homedir.glob("*.*")
                if f.is_file()
                and f.name.lower().endswith((".jpg", ".jpeg", ".png"))
                and not f.name.startswith(".")
            ],
            key=lambda f: f.stem,
        )
        if self.imagelist:
            self.img_height, self.img_width = self.read_image(0).shape[:2]
        return self

    def read_image(self, index: int) -> ndarray:
        if index < 0 or index > len(self.imagelist) - 1:
            raise IndexError()
        return cv2.imread(os.fspath(self.imagelist[index]))

    def create_task_queue(
        self,
        start: int,
        end: int,
        slicestep: int,
    ) -> Tuple[int, mp.Queue]:
        task = mp.Queue()
        step_num = range(start, end + 1, slicestep)
        for num, (img1, img2) in enumerate(zip(step_num[:-1], step_num[1:])):
            task.put_nowait(
                Task(
                    num,
                    os.fspath(self.imagelist[img1]),
                    os.fspath(self.imagelist[img2]),
                )
            )
        task.put_nowait(Task())
        return num + 1, task

    def create_list_tasks(
        self,
        start: int,
        end: int,
        slicestep: int,
    ) -> Tuple[int, List[Task]]:
        step_num = range(start, end + 1, slicestep)
        tasks = [
            Task(
                num,
                os.fspath(self.imagelist[img1]),
                os.fspath(self.imagelist[img2]),
            )
            for num, (img1, img2) in enumerate(zip(step_num[:-1], step_num[1:]))
        ]
        return len(tasks), tasks
