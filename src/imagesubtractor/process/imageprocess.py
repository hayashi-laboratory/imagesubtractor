from pathlib import Path
import queue
import threading
from typing import Dict

import pandas as pd

from ..processwindow import ProcessWindow, ProcessWindowCV
from .parallel_subtractor import ParallelSubtractor

__all__ = ["Imageprocess"]


class Imageprocess(threading.Thread):
    def __init__(
        self,
        subtractor: ParallelSubtractor,
        outputdir: Path,
        progress = None,
    ) -> "Imageprocess":
        super().__init__()

        self.subtractors = subtractor
        self.outputfile = Path(outputdir).joinpath("area.csv")
        self.progress = progress
        self.queue = queue.Queue()
    
    def current_progress_num(self):
        return self.queue.get() 

    def run(self):
        self.subtractors.start()
        with open(self.outputfile, mode = "w", encoding="utf-8") as file:
            header = ""
            while True:
                i, subtmedimg, areadata = self.subtractors.retrieve()
                self.queue.put(i)
                if i is None:
                    break
                if not header:
                    header = "idx," + ",".join("Area" for _ in range(len(areadata))) + ",\n"
                    file.write(header)
                data_str = ",".join(map(str, areadata.flatten()))
                row_str = f"{i},{data_str},\n"
                file.write(row_str)
                if self.progress is not None:
                    self.progress.setValue(self.progress.value()+1)

        df = pd.read_csv(self.outputfile).set_index("idx").sort_index()
        df.to_csv(self.outputfile, index=False, header= ["Area" for _ in df.columns])
        print(f"[SYSTEM] area.csv was saved at {self.outputfile}" )