from datetime import datetime
from utils.dt import DT, JST


def test_convert_slashdate_to_datetime():
    TERAKOYA_START_TIME = 17
    assert DT.convert_slashdate_to_datetime("07/19 (火)") == datetime(
        year=DT.CURRENT_JST_DATETIME.year,
        month=7,
        day=19,
        hour=TERAKOYA_START_TIME,
        tzinfo=JST
    )
    assert DT.convert_slashdate_to_datetime("5/3 (火)") == datetime(
        year=DT.CURRENT_JST_DATETIME.year,
        month=5,
        day=3,
        hour=TERAKOYA_START_TIME,
        tzinfo=JST
    )


def test_convert_iso_to_slushdate():
    assert DT.convert_iso_to_slushdate("2023-01-31") == "01/31"
    # assert DT.convert_iso_to_slushdate("2023-01-31") == "1/31" # NG
