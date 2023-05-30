import os
import sys
import json
import requests

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(ROOT_DIR_PATH)

from functions.handlers.book import BookingRequest
from functions.models.booking import TERAKOYA_TYPE_TO_PLACE_MAP, BookingItem, TERAKOYA_TYPE
from functions.domain.booking import BookingTable, generate_sk

from tests.utils.const import base_url, headers
from tests.samples.booking import book_request_body_json, email, terakoya_type_value, attendance_date_list


class TestAPIGateway:
    """
    Grouping multiple tests in a class
    https://docs.pytest.org/en/7.1.x/getting-started.html#group-multiple-tests-in-a-class
    https://zenn.dev/ymiz/articles/c25dcddfedd7c3
    """

    __target_date = "3000-01-28"

    def __book(self, terakoya_type: TERAKOYA_TYPE) -> requests.Response:
        # Unless specifying Content-Type, the request body is not recognized as JSON and decoded as a string incorrectly in Lambda
        return requests.post(f"{base_url}/book", headers=headers, data=json.dumps({**book_request_body_json, "attendance_date_list": [self.__target_date], "terakoya_type": terakoya_type.value}))

    def test_place_for_terakoya_type(self):
        # https://www.qbook.jp/column/633.html
        """Black-box testing for /book"""
        for terakoya_type in TERAKOYA_TYPE:
            response = self.__book(terakoya_type)
            print(response)
            response_body = response.json()
            print(response_body)
            assert response.status_code == 200
            assert response_body.get("status_code") == 200
            bk_item = BookingItem(**BookingTable.get_item(self.__target_date, email, terakoya_type))
            assert bk_item.place == TERAKOYA_TYPE_TO_PLACE_MAP[terakoya_type]


def test_func():
    # https://hnavi.co.jp/knowledge/blog/white-box-test/
    """White-box testing for /book"""
    booking_request = BookingRequest({**book_request_body_json})

    # List comprehension is better to do the same thing as Array.map(obj => obj.prop) in JavaScript rather than using map(lambda x: x.prop, list)
    # https://blog.utgw.net/entry/2017/03/09/154314
    date_list = [bk_item.date for bk_item in booking_request.booking_item_list]
    # Check whether the same number of booking items are created as the number of attendance dates
    assert attendance_date_list[0] in date_list
    assert attendance_date_list[1] in date_list
    assert attendance_date_list[2] in date_list

    # Some of props are only tested by equivalence partitioning
    # https://e-words.jp/w/%E5%90%8C%E5%80%A4%E5%88%86%E5%89%B2.html
    assert booking_request.booking_item_list[0].email == email
    assert booking_request.booking_item_list[0].terakoya_type.value == terakoya_type_value

    # White-box testing for BookingItem's __init__()
    assert booking_request.booking_item_list[0].place.value == TERAKOYA_TYPE_TO_PLACE_MAP[TERAKOYA_TYPE(
        terakoya_type_value)].value
    assert booking_request.booking_item_list[0].sk == generate_sk(email, TERAKOYA_TYPE(terakoya_type_value))

    booking_request.book()

    booked_item = BookingTable.get_item(date_list[0], email, TERAKOYA_TYPE(terakoya_type_value))
    bk_item = BookingItem(**booked_item)

    # Test for booking completion
    assert bk_item.timestamp == booking_request.booking_item_list[0].timestamp
    assert bk_item.uid == booking_request.booking_item_list[0].uid
