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

    def to_dict(self) -> dict:
        return {
            "uuid": self.uuid,
            "type": self.type,
        }


class BaseTimelineItem(BaseModel):
    uuid: str
    """UID of user who posted/commented"""
    timestamp: int
    """Timestamp of post/comment"""
    user_name: str = ""
    """Nick name of user who posted/commented"""
    user_profile_img_url: str = ""
    """URL of user profile image uploaded to S3"""
    texts: str = ""
    """Texts of post/comment"""
    reactions: List[Reaction] = []
    """List of Reaction"""
    is_deleted: int = 0
    """0: not deleted, 1: deleted"""


class CommentItem(BaseTimelineItem):
    post_id: str
    """Parent post id"""
    comment_id: str
    """UID of comment"""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.comment_id = uuid.uuid4().hex
        self.timestamp = int(DT.CURRENT_JST_DATETIME.timestamp())


class PostItem(BaseTimelineItem):
    comment_count: int = 0
    """List of comment_id"""
    post_id: str
    """UID of post (used for URL)"""
    pk_for_all_post_gsi: str = PK_FOR_ALL_POST_GSI
    """Partition key for GSI"""

    # __init__ method is required to convert DynamoDB item to Pydantic model.
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # The same value is used by all instances of PostItem during the same process if uuid.uuid4().hex is set in class level.
        # Lambda process for production runs longer than development environment.
        # uuid.uuid4() generates random UUID.
        # https://yumarublog.com/python/uuid/
        # .hex returns UUID string without hyphens.
        # https://www.python.ambitious-engineer.com/archives/1436
        self.post_id = uuid.uuid4().hex
        self.timestamp = int(DT.CURRENT_JST_DATETIME.timestamp())
