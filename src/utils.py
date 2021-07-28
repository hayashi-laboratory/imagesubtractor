import os
import json
import datetime

def load_json(path:str)-> dict:
    json_dict = None
    try:
        with open(str(path), mode = "r") as jsonfile:
            json_dict = json.load(jsonfile)
        return json_dict
    except Exception as e:
        print("[ERROR] %s" % e)

def dump_json(path:str, data:dict):
    with open(path, mode = "w") as file:
        json.dump(data, file, indent = 4)


def getTime()->str:
    return datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S')

def fileScanner(path):
    with os.scandir(path) as dircontents:
        for file in dircontents:
            if not file.is_file() or file.name.startswith("."):
                    continue
            else:
                yield file