import os
import sys
import json
from pydantic import BaseModel

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from domain.booking import BookingTable, generate_sk
from models.booking import TERAKOYA_TYPE, PLACE
from utils.process import lambda_handler_wrapper


class EditRequest(BaseModel):
    date: str
    email: str
    terakoya_type: TERAKOYA_TYPE
    place: PLACE

    def update_place(self):
        sk = generate_sk(self.email, self.terakoya_type)
        BookingTable.update_place(self.date, sk, self.place)


def lambda_handler(event, context):
    return lambda_handler_wrapper(event, EditRequest(**json.loads(event['body'])).update_place)
