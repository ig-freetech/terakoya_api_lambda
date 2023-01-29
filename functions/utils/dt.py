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
