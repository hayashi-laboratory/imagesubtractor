import functools
import multiprocessing as mp
import os
import threading
from typing import List

from .queue_item import Result, Task
from .roicollection import RoiCollection
from .subtractor import Subtractor
from .worker import SubtractorWorker, subtract_worker_func

__all__ = ["ParallelSubtractor", "PoolSubtractor"]


class ParallelSubtractor(threading.Thread):
    def __init__(
        self,
        num_workers: int = min(os.cpu_count() - 1, 3),
    ) -> None:
        super().__init__(daemon=True)
        self.output_queue: mp.Queue = mp.Queue()
        self.num_workers = num_workers
        self.workers = []

    def setup_workers(
        self,
        processnum: int,
        tasks: mp.Queue,
        roicollection: RoiCollection,
        threshold: float,
        normalized: bool,
        saveflag: bool = False,
    ) -> "ParallelSubtractor":

        self.processnum = processnum
        self.roinum = len(roicollection)
        self.workers = [
            SubtractorWorker(
                tasks,
                self.output_queue,
                roicollection,
                subtractor=Subtractor(threshold, normalized),
                saveflag=saveflag,
            )
            for _ in range(self.num_workers)
        ]
        return self

    def run(self):
        try:
            for p in self.workers:
                p.start()
            for p in self.workers:
                p.join()
        except Exception as e:
            print(e)
            self.kill_workers()
        finally:
            self.output_queue.put(Result())

    def retrieve(self) -> Result:
        return self.output_queue.get()

    def empty(self) -> bool:
        return self.output_queue.qsize() == 0

    def kill_workers(self) -> None:
        try:
            self.output_queue.put(Result())
            for p in self.workers:
                p.kill()
        except Exception as e:
            print(e)


class PoolSubtractor(threading.Thread):
    def __init__(
        self,
        num_workers: int = min(os.cpu_count() - 1, 3),
    ):
        super().__init__(daemon=True)
        self.output_queue: mp.Queue = mp.Queue()
        self.num_workers = num_workers
        self.process_func = None
        self.tasks = []

    def setup_pool(
        self,
        processnum: int,
        tasks: List[Task],
        roicollection: RoiCollection,
        threshold: float,
        normalized: bool,
        saveflag: bool = False,
    ) -> "PoolSubtractor":

        self.processnum = processnum
        self.roinum = len(roicollection)
        self.process_func = functools.partial(
            subtract_worker_func,
            roicollection=roicollection,
            subtractor=Subtractor(threshold, normalized),
            saveflag=saveflag,
        )
        self.isRunning = False
        self.tasks = tasks
        return self

    def run(self):
        if self.process_func is None:
            raise ValueError("Did not set up the pool function!")

        self.isRunning = True
        with mp.Pool(self.num_workers) as pool:
            results = (pool.apply_async(self.process_func, (t,)) for t in self.tasks)

            for res in results:
                if not self.isRunning:
                    pool.terminate()
                    break
                self.output_queue.put(res.get())

        self.output_queue.put(Result())

    def retrieve(self) -> Result:
        try:
            return self.output_queue.get()
        except Exception as e:
            print(e)
            return Result()

    def empty(self) -> bool:
        return self.output_queue.qsize() == 0

    def kill_workers(self):
        self.isRunning = False
