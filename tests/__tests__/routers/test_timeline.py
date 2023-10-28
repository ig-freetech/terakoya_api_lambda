import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.domain import timeline
from functions.models.timeline import PostItem

TEST_USER_UUID = "d0564635-3a8b-40d5-8ae9-057434a46b8a"


class Test:
    def test_func_post_timeline(self):
        timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": TEST_USER_UUID,
                "user_name": "test-user-name",
                "texts": "test content",
            })
        )

    def test_func_fetch_timeline_list(self):
        response = timeline.fetch_timeline_list()
        print(f"response: {response}")
        assert response.get("items") is not None
        assert response.get("last_evaluated_key") is None
