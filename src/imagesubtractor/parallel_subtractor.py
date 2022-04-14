import os
import threading
import multiprocessing as mp
from typing import Generator, Tuple

import numpy as np

from .roicollection import RoiCollection

from .subtractor import Subtractor, SubtractorWorker


class ParallelSubtractor(threading.Thread):
    def __init__(
        self,
        num_workers: int = os.cpu_count()//2,
    ):
        super().__init__(daemon=True)
        self.output_queue = mp.Queue()
        self.num_workers = num_workers
        self.workers = []

    def setup_workers(
        self,
        image_queue: mp.Queue,
        roicollection: RoiCollection,
        threshold: float,
        normalized: bool,
        saveflag:bool=False,
    ) -> "ParallelSubtractor":
        if self.output_queue is None:
            raise ValueError("output_queue is not set, please run setup_output ")
        self.workers = [
            SubtractorWorker(
                image_queue,
                self.output_queue,
                roicollection,
                threshold=threshold,
                subtractor= Subtractor(normalized),
                saveflag=saveflag,
            )
            for _ in range(self.num_workers)
        ]
        return self

    def run(self):
        for p in self.workers:
            p.start()
        for p in self.workers:
            p.join()
        self.output_queue.put((None, None, None))

    def retrieve(self)->Tuple[int,np.ndarray, np.ndarray]:
        return self.output_queue.get()

    def empty(self)->bool:
        return self.output_queue.qsize() == 0