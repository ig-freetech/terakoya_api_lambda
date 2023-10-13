import os
import sys
import uuid
from typing import Any, List
from pydantic import BaseModel

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.dt import DT

PK_FOR_ALL_POST_GSI = "pk_for_all_post_gsi"


class Reaction(BaseModel):
    uuid: str
    type: int
    """1: like, 2: bad"""


class BaseTimelineItem(BaseModel):
    uuid: str
    """UID of user who posted/commented"""
    timestamp: int = int(DT.CURRENT_JST_DATETIME.timestamp())
    """Sort Key: Timestamp of post/comment"""
    user_name: str = ""
    """Nick name of user who posted/commented"""
    user_profile_img_url: str = ""
    """URL of user profile image uploaded to S3"""
    texts: str = ""
    """Texts of post/comment"""
    reactions: List[Reaction] = []


class CommentItem(BaseTimelineItem):
    post_id: str
    """Partion Key: Parent post id"""
    comment_id: str = uuid.uuid4().hex
    """UID of comment"""
    pk_for_all_post_gsi: str = PK_FOR_ALL_POST_GSI

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)


class PostItem(BaseTimelineItem):
    comment_count: int = 0
    """List of comment_id"""
    # uuid.uuid4() generates random UUID.
    # https://yumarublog.com/python/uuid/
    # .hex returns UUID string without hyphens.
    # https://www.python.ambitious-engineer.com/archives/1436
    post_id: str = uuid.uuid4().hex
    """UID of post (used for URL)"""

    # __init__ method is required to convert DynamoDB item to Pydantic model.
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
