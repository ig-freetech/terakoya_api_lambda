import os
import sys

FUNCTIONS_DIR_PATH = os.path.dirname(__file__)
sys.path.append(FUNCTIONS_DIR_PATH)

from domain.booking import BookingTable
from utils.process import lambda_handler_wrapper_with_rtn_value


def func(event) -> dict:
    # How to get a query parameter value
    # https://qiita.com/minsu/items/c9e983f109b1cf5a516e
    target_date = event['queryStringParameters']['date']
    item_list = BookingTable.get_item_list(target_date)
    return {"item_list": item_list}


def lambda_handler(event, context):
    print(f"Request: {event}")
    # lambda args: return value (ex: lambda n: n * 2, lambda: "Hello World", lambda text: print(text))
    # https://qiita.com/nagataaaas/items/531b1fc5ce42a791c7df
    # lambda is anonymous function as arrow function in JavaScript but it can't be used to define a function more than two lines.
    # https://qiita.com/masaru/items/48ee394640400f0f0d1c
    return lambda_handler_wrapper_with_rtn_value(event, lambda: func(event))
