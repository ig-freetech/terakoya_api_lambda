import os
import sys
import json
import requests

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(ROOT_DIR_PATH)

from functions.domain.booking import BookingTable
from functions.models.booking import BookingItem, TERAKOYA_TYPE, PLACE

from tests.utils.const import base_url, headers
from tests.samples.booking import book_request_body_json, email


class TestAPIGateway:
    def __get_booked_item(self, target_date: str, terakoya_type_value: int) -> BookingItem:
        booked_item = BookingTable.get_item(target_date, email, TERAKOYA_TYPE(terakoya_type_value))
        return BookingItem(**booked_item)

    def test_place_after_edit(self):
        """Black-box testing for /booking/edit/place"""
        target_date = "4000-01-11"
        terakoya_type_value = TERAKOYA_TYPE.HIGH_IKE.value
        requests.post(f"{base_url}/book", headers=headers, data=json.dumps({
            **book_request_body_json, "attendance_date_list": [target_date], "terakoya_type": terakoya_type_value
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

        bk_item = self.__get_booked_item(target_date, terakoya_type_value)
        assert bk_item.place.value == target_place_value
