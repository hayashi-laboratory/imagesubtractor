import queue
import threading
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from .parallel_subtractor import ParallelSubtractor

__all__ = ["Imageprocess"]


class Imageprocess(threading.Thread):
    def __init__(
        self,
        subtractor: ParallelSubtractor,
        outputdir: Path,
    ) -> "Imageprocess":
        super().__init__()

        self.subtractors = subtractor
        self.outputfile = Path(outputdir).joinpath("area.csv")
        self.queue = queue.Queue()

    def processing(self):
        return self.queue.get()

    def run(self):
        self.subtractors.start()
        outputarr = np.zeros(
            (
                self.subtractors.processnum,
                self.subtractors.roinum,
            ),
            dtype=int,
        )
        while True:
            i, subtmedimg, areadata = self.subtractors.retrieve()
            if i is None:
                self.queue.put(False)
                break
            self.queue.put(True)
            outputarr[i] = areadata

        pd.DataFrame(outputarr).to_csv(
            self.outputfile,
            index=False,
            header=["Area" for _ in range(self.subtractors.roinum)],
        )
        print(f"[SYSTEM] area.csv was saved at {self.outputfile}")
