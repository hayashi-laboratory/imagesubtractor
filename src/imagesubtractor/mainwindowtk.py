import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import NamedTuple, Optional

from imagesubtractor.parallel_subtractor import ParallelSubtractor
from imagesubtractor.roicollection import RoiCollection

from imagesubtractor.imagestack import Imagestack

class RoiDefault(NamedTuple):
    box_width:int =100
    box_height:int = 100
    colnum:int = 8
    rownum:int = 6
    topleftx:int = 23
    toplefty:int =49
    intervalx:int =123
    intervaly:int =123
    rotate:int = 0
    slicestep:int = 1

class MainFrameTk(tk.Frame):
    droi = RoiDefault()
    def __init__(self, master=None):
        super().__init__(master)
        self.grid()
        self.stack:Optional[Imagestack] = None
        self.master.title("Imagesubtractor")
        self.setup_frame_size()
        self.createWidgets()
    
    def createWidgets(self):
        self.openBtn = tk.Button(self, text = "Open", command = self.ask_directory)
        self.openBtn.grid()
        self.saveBtn = tk.Button(self, text = "Save", command= self.save_data)
        self.saveBtn.grid()

    def setup_frame_size(self):
        WIDTH, HEIGHT = 600, 400
        posx = (self.master.winfo_screenwidth() - WIDTH) // 2
        posy = (self.master.winfo_screenheight() - HEIGHT) // 2
        self.master.wm_geometry(f"{WIDTH}x{HEIGHT}+{posx}+{posy}")
        self.update()

    def ask_directory(self):
        homedir = filedialog.askdirectory(initialdir=os.getcwd())
        if not homedir:
            return
        homedir = Path(homedir).resolve()
        filelist = [
            f
            for f in homedir.glob("*.*")
            if f.is_file()
            and not f.name.startswith(".")
        ]
        imgnamelist = [f.name for f in filelist if f.name.lower().endswith((".jpg", ".jpeg", ".png"))]
        jsonfiles = [f for f in filelist if f.name.endswith(".json")]
        if jsonfiles:
            self.roicol = RoiCollection.from_json(jsonfiles[0])

        if not imgnamelist:
            return
        self.stack = Imagestack().setdir(os.fspath(homedir), imgnamelist)
    
    def setup_roi(self):
        ... 


    def start_process(self):
        if self.stack is None:
            return

        subtractor = ParallelSubtractor().setup_workers(self.stack.get_image_queue(), self.roicol.copy(), threshold, normalized, saveflag)
        subtractor.start()

        
    def save_data(self):
        if not self.stack:
            return
        print(f"save data at {self.stack.imagedir}")