import re
from datetime import datetime, timezone, timedelta

TIME_DIFFERENCE_UTC_JAPAN_HOUR = 9

JST = timezone(timedelta(hours=TIME_DIFFERENCE_UTC_JAPAN_HOUR), "JST")
CURRENT_DATETIME = datetime.now(JST)

TERAKOYA_START_HOUR = 17


def convert_to_datetime(date_str: str) -> datetime:
    # ['MM', 'DD'] の形で抽出
    regDate = re.search(r'\d+/\d+', date_str)
    if(regDate == None):
        raise Exception("Invalid Date Format.")
    month_day_list = regDate.group().split('/')
    month = int(month_day_list[0])
    day = int(month_day_list[1])
    reservedDateTime = datetime(year=CURRENT_DATETIME.year, month=month, day=day, hour=TERAKOYA_START_HOUR, tzinfo=JST)
    return reservedDateTime


def calc_two_dates_diff_days(standard_dt: datetime, compare_dt: datetime):
    diff = standard_dt - compare_dt
    return diff.days


def test():
    converted_dt = convert_to_datetime("7/2 (土)")
    compared_dt = datetime(CURRENT_DATETIME.year, 7, 2, 18, tzinfo=JST)
    diff_days = calc_two_dates_diff_days(converted_dt, compared_dt)
    print(diff_days)


if __name__ == "__main__":
    test()
