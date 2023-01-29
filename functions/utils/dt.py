import re
from datetime import datetime, timezone, timedelta

TIME_DIFFERENCE_UTC_JAPAN_HOUR = 9
JST = timezone(timedelta(hours=TIME_DIFFERENCE_UTC_JAPAN_HOUR), "JST")
current_jst_datetime = datetime.now(JST)

TERAKOYA_START_HOUR = 17


def convert_to_datetime(date_str: str) -> datetime:
    # ['MM', 'DD'] の形で抽出
    regDate = re.search(r'\d+/\d+', date_str)
    if (regDate == None):
        raise Exception("Invalid Date Format.")
    month_day_list = regDate.group().split('/')
    month = int(month_day_list[0])
    day = int(month_day_list[1])
    reservedDateTime = datetime(year=current_jst_datetime.year, month=month,
                                day=day, hour=TERAKOYA_START_HOUR, tzinfo=JST)
    return reservedDateTime


def test():
    converted_dt = convert_to_datetime("07/02 (土)")
    converted_dt_1 = convert_to_datetime("7/2 (土)")
    compared_dt = datetime(current_jst_datetime.year, 7, 2, 18, tzinfo=JST)
    diff_days = (converted_dt - compared_dt).days
    print(diff_days)


def pytest():
    return 'SS'


if __name__ == "__main__":
    test()
