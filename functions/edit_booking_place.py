import os
import sys
import json

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from domain.dynamodb import BookingDynamoDB


def lambda_handler(event, context):
    print(f"Request body: {event['body']}")
    try:
        request_body = json.loads(event['body'])
        date = request_body["date"]
        email = request_body["email"]
        terakoya_type = request_body["terakoya_type"]
        place = request_body["place"]
        sk = f"#{email}#{terakoya_type}"
        BookingDynamoDB().update_place(date, sk, place)
        return {
            'result_type': 1,
            'message': 'Success'
        }
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        return {
            'result_type': 0,
            'message': 'Failed'
        }