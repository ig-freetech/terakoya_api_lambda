import os
import sys
import json
from typing import Dict

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)


def get_dic_from_json(json_fpath):
    dic: Dict[str, str]
    with open(json_fpath) as f:
        dic = json.load(f)
    return dic


if __name__ == "__main__":
    print("test")
