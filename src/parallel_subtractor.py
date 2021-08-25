import os
import threading
import multiprocessing as mp
from .subtractor import SubtractorWorker
from .imagestack import Imagestack


class ParallelSubtractor(threading.Thread):
    def __init__(
        self,
        start: int,
        end: int,
        slicestep: int,
        imagestack: Imagestack,
        output_queue,
        threshold,
        normalized=False,
        num_workers=None,
        daemon=True,
    ):
        super().__init__(daemon=daemon)
        self.output_queue = output_queue
        self.input_queue = self.set_input_queue(start, end, slicestep, imagestack)
        self.num_workers = num_workers or os.cpu_count()
        self.processors = [
            SubtractorWorker(
                self.input_queue,
                self.output_queue,
                threshold=threshold,
                normalized=normalized,
                daemon=daemon,
            )
            for _ in range(self.num_workers)
        ]

    def set_input_queue(
        self,
        start: int,
        end: int,
        slicestep: int,
        imagestack: Imagestack,
    ):
        queue = mp.Queue()
        imagedir = imagestack.imagedir
        imagenamelist = imagestack.imagenamelist
        step_num = range(start, end, slicestep)
        for i, (current, next) in enumerate(zip(step_num[:-1], step_num[1:])):
            queue.put_nowait(
                (
                    i,
                    os.path.join(imagedir, imagenamelist[current]),
                    os.path.join(imagedir, imagenamelist[next]),
                )
            )
        queue.put_nowait((None, None, None))
        return queue

    def run(self):
        for p in self.processors:
            p.start()
        for p in self.processors:
            p.join()
        self.output_queue.put((None, None, None))
