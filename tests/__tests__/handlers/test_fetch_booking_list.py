import os
import sys
import requests
from typing import List


ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(ROOT_DIR_PATH)

from functions.domain.booking import BookingTable
from functions.models.booking import BookingItem, TERAKOYA_TYPE

from tests.samples.booking import booking_item_json
from tests.utils.const import base_url, headers


class TestAPIGateway:
    def test_fetch_booking_item_list(self):
        """Black-box testing for /booking/list"""
        target_date = "3000-02-11"
        booking_item_json_list = [
            {**booking_item_json, "date": target_date},
            # Delete key itself from dict with dict comprehension
            # https://note.nkmk.me/python-dict-clear-pop-popitem-del/
            {k: v for k, v in {
                **booking_item_json,
                "date": target_date,
                "terakoya_type": TERAKOYA_TYPE.ONLINE_TAMA.value
            }.items() if k != "sk"},
        ]
        for bk_item_json in booking_item_json_list:
            BookingTable.insert_item(BookingItem(**bk_item_json))
        response = requests.get(f"{base_url}/booking/list?date={target_date}", headers=headers)
        print(response)
        response_body = response.json()
        print(response_body)
        assert response.status_code == 200
        assert response_body.get("item_list") is not None
        item_list: List = response_body.get("item_list")
        assert len(item_list) == len(booking_item_json_list)
