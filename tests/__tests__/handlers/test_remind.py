import os
import sys
import pytest
from datetime import datetime

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(ROOT_DIR_PATH)

from functions.handlers.booking.remind import remind
from functions.domain.booking import BookingTable
from functions.models.booking import BookingItem, TERAKOYA_TYPE, REMIND_STATUS, PLACE
from functions.utils.dt import DT

from tests.samples.booking import booking_item_json


def is_tuesday_or_saturday(date: datetime):
    # 1: Monday, 2: Tuesday, ..., 6: Saturday, 7: Sunday
    weekday = date.weekday() + 1
    print(f"Today is {weekday}")
    return weekday in [2, 6]


# Can skip a test with pytest.mark.skipif(condition, reason_text)
# https://webbibouroku.com/Blog/Article/pytest-skip
@pytest.mark.skipif(
    is_tuesday_or_saturday(DT.CURRENT_JST_DATETIME),
    reason="Skips the test because today is on Tuesday or Saturday"
)
def test_remind():
    """Black-box testing for sending reminder email"""
    target_date = DT.CURRENT_JST_ISO_8601_ONLY_DATE
    common_bk_item_json = {**booking_item_json, "date": target_date, "is_reminded": REMIND_STATUS.NOT_SENT.value}
    booking_item_json_list = [
        {**common_bk_item_json, "sk": "test_remind_sk1"},
        {**common_bk_item_json, "sk": "test_remind_sk2", "terakoya_type": TERAKOYA_TYPE.ONLINE_TAMA.value},
        {**common_bk_item_json, "sk": "test_remind_sk3",
            "terakoya_type": TERAKOYA_TYPE.MID_IKE.value, "place": PLACE.BASE_CAMP.value},
        {**common_bk_item_json, "sk": "test_remind_sk4",
            "terakoya_type": TERAKOYA_TYPE.HIGH_IKE.value, "place": PLACE.SUNSHINE.value},
    ]
    for bk_item_json in booking_item_json_list:
        BookingTable.insert_item(BookingItem(**bk_item_json))

    item_list = [BookingItem(**bk_item_json) for bk_item_json in BookingTable.get_item_list(target_date)]
    assert item_list[0].is_reminded.value == REMIND_STATUS.NOT_SENT.value
    assert item_list[0].place.value == PLACE.TBD.value
    assert item_list[1].is_reminded.value == REMIND_STATUS.NOT_SENT.value
    assert item_list[1].place.value == PLACE.CAREER_MOM.value
    assert item_list[2].is_reminded.value == REMIND_STATUS.NOT_SENT.value
    assert item_list[2].place.value == PLACE.BASE_CAMP.value
    assert item_list[3].is_reminded.value == REMIND_STATUS.NOT_SENT.value
    assert item_list[3].place.value == PLACE.SUNSHINE.value

    remind()

    item_list = [BookingItem(**bk_item_json) for bk_item_json in BookingTable.get_item_list(target_date)]
    assert len(item_list) == len(booking_item_json_list)
    assert item_list[0].is_reminded.value == REMIND_STATUS.NOT_SENT.value
    assert item_list[1].is_reminded.value == REMIND_STATUS.SENT.value
    assert item_list[2].is_reminded.value == REMIND_STATUS.SENT.value
    assert item_list[3].is_reminded.value == REMIND_STATUS.SENT.value
