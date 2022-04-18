from pathlib import Path
import queue
from PySide2 import QtCore, QtWidgets
from tqdm import tqdm
from ..process import Imageprocess, ParallelSubtractor


class QThreadWorker(QtCore.QThread):
    process_result = QtCore.Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def set_params(
        self,
        outputdir: Path,
        subtractors: ParallelSubtractor,
    ) -> "QThreadWorker":
        self.outputdir = outputdir
        self.subtractors = subtractors
        self.display = queue.Queue()
        return self

    def run(self):
        self.ip = Imageprocess(
            subtractor=self.subtractors,
            outputdir=self.outputdir,
        )
        self.ip.start()
        with tqdm(
            desc=f"[{self.outputdir}]", total=self.subtractors.processnum
        ) as tbar:
            count = 0
            cache = {}
            while True:
                i, img = self.ip.retrieve()
                if i is None:
                    break
                cache[i] = img
                if count in cache:
                    self.process_result.emit(cache.pop(count))
                    tbar.update()
                    count += 1
            while count in cache:
                self.process_result.emit(cache.pop(count))
                count += 1
                tbar.update()

        self.ip.join()
        self.process_result.emit(None)
