import os
import sys
from typing import Any, List
from enum import Enum
from decimal import Decimal
from pydantic import BaseModel

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.dt import DT

EMPTY_SK = "EMPTY_SK"


class GRADE(Enum):
    """学年 (grade)"""
    HIGH_SCHOOL_1 = 1
    """高校1年生"""
    HIGH_SCHOOL_2 = 2
    """高校2年生"""
    HIGH_SCHOOL_3 = 3
    """高校3年生"""
    JUNIOR_HIGH_SCHOOL_1 = 11
    """中学1年生"""
    JUNIOR_HIGH_SCHOOL_2 = 12
    """中学2年生"""
    JUNIOR_HIGH_SCHOOL_3 = 13
    """中学3年生"""
    OTHER = 0
    """その他"""
    NULL = -1
    """未選択"""


class COURSE_CHOICE(Enum):
    """文理選択 (course_choice)"""
    TBD = 1
    """まだ決めていない"""
    LIBERAL_ARTS = 2
    """文系"""
    SCIENCE = 3
    """理系"""
    OTHER = 0
    """その他"""
    NULL = -1
    """未選択"""


class HOW_TO_KNOW_TERAKOYA(Enum):
    """テラコヤを知ったきっかけ (how_to_know_terakoya)"""
    HP = 1
    """HP"""
    INSTAGRAM = 2
    """Instagram"""
    FACEBOOK = 3
    """Facebook"""
    TWITTER = 4
    """Twitter"""
    INTRODUCE = 5
    """知人の紹介"""
    POSTER = 6
    """ポスター・ビラ"""
    OTHER = 0
    """その他"""
    NULL = -1
    """未選択"""


class UserItem(BaseModel):
    uuid: str
    # アカウント登録時にStepを2つ用意してStep1でユーザータイプを選択させる？ (sk: student, company, admin, staff)
    # Set a dummy value to sort key by default because Sort key can't be empty string.
    # For now, there's no value to be set as sort key when a user signs up.
    sk: str = EMPTY_SK  # TODO: Replace a dummy value with a proper value in the future.
    email: str

    # The following fields are optional because they are not required when a user signs up. After signing up, a user can update these fields.
    # Profile fields
    name: str = ""
    nickname: str = ""
    school: str = ""
    grade: GRADE = GRADE.NULL
    course_choice: COURSE_CHOICE = COURSE_CHOICE.NULL
    staff_in_charge: List[str] = []
    future_path: str = ""
    like_thing: str = ""
    how_to_know_terakoya: HOW_TO_KNOW_TERAKOYA = HOW_TO_KNOW_TERAKOYA.NULL
    # Analytics fields
    number_of_attendances: int = 0
    attendance_rate: float = 0.0
    # Authority fields
    is_admin: bool = False
    # Timestamp fields
    created_at_iso: str = DT.CURRENT_JST_ISO_8601_DATETIME
    updated_at_iso: str = ""

    # __init__ method is required to convert DynamoDB item to Pydantic model.
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def to_dynamodb_item(self):
        # Convert Enum to its value
        item_dict = {k: v.value if isinstance(v, Enum) else v for k, v in self.__dict__.items()}
        # DynamoDB doesn't accept float type. So, convert float to Decimal.
        item_dict["attendance_rate"] = Decimal(str(item_dict["attendance_rate"]))
        return item_dict
