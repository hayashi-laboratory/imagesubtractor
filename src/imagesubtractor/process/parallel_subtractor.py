import multiprocessing as mp
import os
import threading

from .queue_item import Result
from .roicollection import RoiCollection
from .subtractor import Subtractor
from .worker import SubtractorWorker

__all__ = ["ParallelSubtractor"]


class ParallelSubtractor(threading.Thread):
    def __init__(
        self,
        num_workers: int = min(os.cpu_count(), 4),
    ):
        super().__init__(daemon=True)
        self.output_queue: mp.Queue = mp.Queue()
        self.num_workers = num_workers
        self.workers = []

    def setup_workers(
        self,
        processnum: int,
        task: mp.Queue,
        roicollection: RoiCollection,
        threshold: float,
        normalized: bool,
        saveflag: bool = False,
    ) -> "ParallelSubtractor":

        self.processnum = processnum
        self.roinum = len(roicollection)
        self.workers = [
            SubtractorWorker(
                task,
                self.output_queue,
                roicollection,
                subtractor=Subtractor(threshold, normalized),
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
        self.output_queue.put(Result())

    def retrieve(self) -> Result:
        return self.output_queue.get()

    def empty(self) -> bool:
        return self.output_queue.qsize() == 0
