import datetime
import json
import os
import time
from contextlib import contextmanager
from typing import Callable, Dict


@contextmanager
def timer(display: Callable = None):
    if not callable(display):
        display = print
    t1 = time.perf_counter()
    display(f"[SYSTEM] Start at: {get_time()}")
    yield
    display(f"[SYSTEM] End at: {get_time()}")
    display(f"[SYSTEM] Elapse: {time.perf_counter() - t1:.2f} (Sec)")


def load_json(path: str) -> Dict:
    json_dict = None
    try:
        with open(path, mode="r") as file:
            json_dict = json.load(file)
        return json_dict
    except Exception as e:
        print("[ERROR] %s" % e)


def dump_json(path: str, data: dict) -> None:
    with open(path, mode="w") as file:
        json.dump(data, file, indent=4)


def get_time() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H:%M:%S")


def glob_files(path):
    with os.scandir(path) as dircontents:
        for file in dircontents:
            if not file.is_file() or file.name.startswith("."):
                continue
            else:
                yield file
