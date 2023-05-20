import hashlib
import os
import sys
from typing import List, Any
from pydantic import BaseModel, EmailStr, Field, validator

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.dt import DT

# Define a private member with '__' prefix
# https://rinatz.github.io/python-book/ch03-02-scopes/

# Difference between private and protected member
# https://www.nblog09.com/w/2019/01/09/python-protected-private/


class __CommonProperties(BaseModel):
    name: str
    # Check whether the email format is valid based on RFC 5322 using EmailStr type
    # https://qiita.com/koralle/items/93b094ddb6d3af917702#emailstr
    # https://docs.pydantic.dev/latest/usage/types/#pydantic-types
    # https://qiita.com/yoshitake_1201/items/40268332cd23f67c504c
    email: EmailStr
    # Field(ge=min_value, le=max_value) is used to validate the value of the field
    # https://blog.monorevo.jp/pydantic-model-validation
    # 1: カフェ塾テラコヤ(池袋), 2: オンラインテラコヤ(多摩), 3: テラコヤ中等部(池袋), 4: テラコヤ中等部(渋谷), 0: その他
    terakoya_type: int = Field(..., ge=0, le=4)
    # 1: 17:00前, 2: 17:00~17:30, 3: 17:30~18:00, 4: 18:00以降, 0: その他
    arrival_time: int = Field(..., ge=0, le=4)
    # 1: 高校1年生, 2: 高校2年生, 3: 高校3年生, 11: 中学1年生, 12: 中学2年生, 13: 中学3年生, 0: その他
    grade: int = Field(..., ge=0, le=13)
    # 1: 今回が初回, 2: 過去に参加したことがある, 0: その他
    terakoya_experience: int = Field(..., ge=0, le=2)
    # 1: 英語, 2: 国語, 3: 数学, 4: 社会, 5: 理科, 6: 推薦型入試対策（志望理由書・面接など）, 7: 大学説明会, 8: キャリア説明会, 9: 英検, 0: その他
    study_subject: int = Field(..., ge=0, le=9)
    study_subject_detail: str
    # 1: 黙々と静かに勉強したい, 2: 分からない点があったらスタッフに質問したい, 3: 友達と話しながら楽しく勉強したい, 4: 1人では難しいのでスタッフ付きっ切りで勉強を教えて欲しい, 5: 勉強も教えて欲しいけどスタッフの話を聞いたり、相談したい。, 0: その他, -1: 未設定
    study_style: int = Field(..., ge=-1, le=5)
    school_name: str
    first_choice_school: str
    # 1: まだ決めていない, 2: 文系, 3: 理系, 0: その他, -1: 未設定
    course_choice: int = Field(..., ge=-1, le=3)
    future_free: str
    like_thing_free: str
    # 1: HP, 2: Instagram, 3: Facebook, 4: Twitter, 5: 知人の紹介, 6: ポスター、ビラ, 0: その他, -1: 未設定
    how_to_know_terakoya: int = Field(..., ge=-1, le=6)
    remarks: str

    @validator('grade')
    # https://docs.pydantic.dev/latest/usage/validators/
    def grade_values(cls, v):
        if v not in [1, 2, 3, 11, 12, 13]:
            raise ValueError('grade value must be 1, 2, 3, 11, 12, or 13')
        return v


class BookRequestBody(__CommonProperties):
    """
    Request body sent via API Gateway
    """
    attendance_date_list: List[str]


TERAKOYA_TYPE_TO_PLACE_MAP = {
    0: -1,  # その他 -> NULL
    1: 0,  # カフェ塾テラコヤ(池袋) -> TBD
    2: 4,  # オンラインテラコヤ(多摩) -> キャリア・マム
    3: 1,  # テラコヤ中等部(池袋) -> サンシャインシティ
    4: 5,  # テラコヤ中等部(渋谷) -> キカガク
}


class BookingItem(__CommonProperties):
    """
    Item that is converted from a request body sent via API Gateway and then to be inserted into DynamoDB  
    """
    date: str
    sk: str = ""
    # 0: 未設定, 1: サンシャインシティ, 2: 良品計画本社, 3: DIORAMA CAFE, 4: キャリア・マム, 5: キカガク
    place: int = Field(-1, ge=-1, le=5)
    # 0: 未送信, 1: 送信済み
    is_reminded: int = Field(0, ge=0, le=1)
    timestamp: int = int(DT.CURRENT_JST_DATETIME.timestamp())
    timestamp_iso: str = DT.CURRENT_JST_DATETIME.strftime("%Y-%m-%d %H:%M:%S")
    date_unix_time: int = -1
    uid: str = ""

    # kwargs is a dictionary of arguments. args is a tuple of positional arguments.
    # https://note.nkmk.me/python-args-kwargs-usage/
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.place = TERAKOYA_TYPE_TO_PLACE_MAP[self.terakoya_type]
        self.sk = f"#{self.email}#{self.terakoya_type}"
        self.date_unix_time = DT.convert_iso_to_timestamp(self.date)
        self.uid = hashlib.md5(f"#{self.date}{self.sk}".encode()).hexdigest()
