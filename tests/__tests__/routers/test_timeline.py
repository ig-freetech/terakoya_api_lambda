import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.domain import timeline


class Test:
    def test_func_fetch_timeline_list(self):
        # response = timeline.fetch_timeline_list()
        # print(f"response: {response}")
        # assert response.get("items") is not None
        # assert response.get("last_evaluated_key") is None
        pass
