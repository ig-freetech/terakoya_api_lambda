from pydantic import BaseModel

EMPTY_SK = "EMPTY_SK"


class UserItem(BaseModel):
    uuid: str
    # アカウント登録時にStepを2つ用意してStep1でユーザータイプを選択させる？ (sk: student, company, admin, staff)
    # Set a dummy value to sort key by default because Sort key can't be empty string.
    # For now, there's no value to be set as sort key when a user signs up.
    sk: str = EMPTY_SK
    email: str
