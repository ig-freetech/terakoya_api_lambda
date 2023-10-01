import os
import sys
import uuid
from typing import List
from pydantic import BaseModel

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.dt import DT


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
    user_profile_img_url: str = ""
    texts: str = ""
    """Texts of post/comment"""
    reactions: List[Reaction] = []


class CommentItem(BaseTimelineItem):
    post_id: str
    """Partion Key: Parent post id"""
    comment_id: str = uuid.uuid4().hex
    """UID of comment"""


class PostItem(BaseTimelineItem):
    comments: List[str] = []
    """List of comment_id"""
    # uuid.uuid4() generates random UUID.
    # https://yumarublog.com/python/uuid/
    # .hex returns UUID string without hyphens.
    # https://www.python.ambitious-engineer.com/archives/1436
    post_id: str = uuid.uuid4().hex
    """UID of post (used for URL)"""
