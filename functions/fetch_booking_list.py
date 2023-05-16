import os
import sys

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from domain.dynamodb import BookingDynamoDB


def lambda_handler(event, context):
    print(f"Request: {event}")
    try:
        # How to get a query parameter value
        # https://qiita.com/minsu/items/c9e983f109b1cf5a516e
        target_date = event['queryStringParameters']['date']
        item_list = BookingDynamoDB.get_item_list(target_date)
        return {
            'result_type': 1,
            'message': 'Success',
            'item_list': item_list
        }
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        return {
            'result_type': 0,
            'message': 'Failed',
        }
