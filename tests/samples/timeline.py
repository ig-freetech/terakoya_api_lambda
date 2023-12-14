import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from tests.samples.user import PYTEST_USER_UUID, PYTEST_USER_NAME


post_timeline_item_json = {
    "uuid": PYTEST_USER_UUID,
    "user_name": PYTEST_USER_NAME,
    # "user_profile_img_url": "",
    "texts": "Post timeline item from pytest via API Gateway",
}

post_comment_item_json = {
    "post_id": "Dummy",  # TODO: to be merged (required)
    "uuid": PYTEST_USER_UUID,
    "user_name": PYTEST_USER_NAME,
    # "user_profile_img_url": "",
    "texts": "Post comment item from pytest via API Gateway",
}

TYPE_LIKE = 1
put_reaction_json = {
    "uuid": PYTEST_USER_UUID,
    "type": TYPE_LIKE,
}