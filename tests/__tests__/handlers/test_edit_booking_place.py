import os
import sys
import json
import requests
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, after_log

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(ROOT_DIR_PATH)

from functions.domain.booking import BookingTable
from functions.models.booking import BookingItem, TERAKOYA_TYPE, PLACE

from tests.utils.const import base_url, headers
from tests.samples.booking import booking_item_json, email, terakoya_type_value


class TestAPIGateway:
    def __get_booked_item(self, target_date: str, terakoya_type_value: int) -> BookingItem:
        booked_item = BookingTable.get_item(target_date, email, TERAKOYA_TYPE(terakoya_type_value))
        return BookingItem(**booked_item)

    # Wait for a few seconds for the updated date to be reflected in the database
    # tenacity enables retrying when the test fails with conditions of timeout secs and interval secs etc...
    # https://ohke.hateblo.jp/entry/2020/11/21/230000
    @retry(stop=stop_after_attempt(2), wait=wait_fixed(5), after=after_log(logging.getLogger(__name__), logging.WARNING))
    def __check_place_updated(self, target_date: str, terakoya_type_value: int, target_place_value: int):
        bk_item = self.__get_booked_item(target_date, terakoya_type_value)
        assert bk_item.place.value == target_place_value

    def test_place_after_edit(self):
        """Black-box testing for /booking/edit/place"""
        target_date = "4000-01-11"
        BookingTable.insert_item(BookingItem(**{
            **booking_item_json, "date": target_date
        }))
        bk_item = self.__get_booked_item(target_date, terakoya_type_value)
        assert bk_item.place.value == PLACE.TBD.value

        target_place_value = PLACE.SUNSHINE.value
        response = requests.put(f"{base_url}/booking/edit/place", headers=headers, data=json.dumps({
            **bk_item.to_dict(), "place": target_place_value})
        )
        print(response)
        response_body = response.json()
        print(response_body)
        assert response.status_code == 200
        assert response_body.get("status_code") == 200

        self.__check_place_updated(target_date, terakoya_type_value, target_place_value)
