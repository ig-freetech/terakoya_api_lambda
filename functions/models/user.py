from pydantic import BaseModel

class UserItem(BaseModel):
    uuid: str
    sk: str = ""
    email: str