import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.domain import timeline
from functions.models.timeline import PostItem

TEST_USER_UUID = "d0564635-3a8b-40d5-8ae9-057434a46b8a"


class Test:
    def test_func_post_timeline(self):
        post_response = timeline.post_timeline_item(
            post=PostItem(**{
                "uuid": TEST_USER_UUID,
                "user_name": "test-user-name",
                "texts": "test content",
            })
        )
        print(f"post_response: {post_response}")
        post_id = post_response.get("post_id")
        assert post_id is not None
        post_item = timeline.fetch_post_item(post_id)
        print(f"post_item: {post_item}")
        assert post_item.get("post_id") == post_id

    def test_func_fetch_timeline_list(self):
        response = timeline.fetch_timeline_list()
        print(f"response: {response}")
        assert response.get("items") is not None
        assert response.get("last_evaluated_key") is None
