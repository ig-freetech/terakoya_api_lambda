import os
import sys
from typing import List
from enum import Enum
from pydantic import BaseModel

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)


class ReactionType(Enum):
    """Types of reaction"""
    NONE = 0
    """No reaction"""
    GOOD = 1
    LOVE = 2
    FUN = 3
    SAD = 4
    ANGRY = 5
    FIRE = 6


class Reaction(BaseModel):
    uuid: str
    type: ReactionType = ReactionType.NONE


class BaseTimelineItem(BaseModel):
    uuid: str
    """UID of user who posted/commented"""
    timestamp: int
    """Sort Key: Timestamp of post/comment"""
    user_name: str = ""
    user_profile_img_url: str = ""
    texts: str = ""
    """Texts of post/comment"""
    reactions: List[Reaction] = []


class CommentItem(BaseTimelineItem):
    post_id: str
    """Partion Key: Parent post id"""
    comment_id: str
    """UID of comment"""


class PostItem(BaseTimelineItem):
    comments: List[str] = []
    """List of comment_id"""
    post_id: str = ""
    """UID of post (used for URL)"""
