from datetime import datetime
from utils.dt import DT, JST


def test_convert_to_datetime():
    assert DT.convert_slashdate_to_datetime("07/19 (火)") == datetime(
        year=DT.CURRENT_JST_DATETIME.year,
        month=7,
        day=19,
        tzinfo=JST
    )
    assert DT.convert_slashdate_to_datetime("5/3 (火)") == datetime(
        year=DT.CURRENT_JST_DATETIME.year,
        month=5,
        day=3,
        tzinfo=JST
    )


if __name__ == "__main__":
    pass
