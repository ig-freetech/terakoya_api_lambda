import os
import sys
import json

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from domain.booking import BookingTable, generate_sk
from utils.process import lambda_handler_wrapper


def lambda_handler(event, context):
    def func():
        request_body = json.loads(event['body'])
        date = request_body["date"]
        email = request_body["email"]
        terakoya_type = request_body["terakoya_type"]
        place = request_body["place"]
        sk = generate_sk(email, terakoya_type)
        BookingTable.update_place(date, sk, place)
    lambda_handler_wrapper(event, func)
