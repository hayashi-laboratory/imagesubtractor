import os
import json
import datetime
from typing import Dict


def load_json(path: str) -> Dict:
    json_dict = None
    try:
        with open(path, mode="r") as file:
            json_dict = json.load(file)
        return json_dict
    except Exception as e:
        print("[ERROR] %s" % e)


def dump_json(path: str, data: dict)->None:
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
