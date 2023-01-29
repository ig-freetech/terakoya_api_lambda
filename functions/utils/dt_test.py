from datetime import datetime
from utils.dt import convert_to_datetime, current_jst_datetime, TERAKOYA_START_HOUR, JST


def test_convert_to_datetime():
    assert convert_to_datetime("07/19 (火)") == datetime(year=current_jst_datetime.year, month=7,
                                                        day=19, hour=TERAKOYA_START_HOUR, tzinfo=JST)
    assert convert_to_datetime("5/3 (火)") == datetime(year=current_jst_datetime.year, month=5,
                                                      day=3, hour=TERAKOYA_START_HOUR, tzinfo=JST)
