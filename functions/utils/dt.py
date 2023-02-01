import os
import sys
import re
from datetime import datetime, timezone, timedelta

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.subclass import classproperty

TIME_DIFFERENCE_UTC_JAPAN_HOUR = 9
JST = timezone(timedelta(hours=TIME_DIFFERENCE_UTC_JAPAN_HOUR), "JST")


class DT:
    @classproperty
    @classmethod
    def CURRENT_JST_DATETIME(cls) -> datetime:
        return datetime.now(JST)

    @classproperty
    @classmethod
    def CURRENT_JST_ISO_8601_ONLY_DATE(cls) -> str:
        return cls.CURRENT_JST_DATETIME.strftime(f"%Y-%m-%d")

    @staticmethod
    def convert_slashdate_to_datetime(date: str) -> datetime:
        # ['MM', 'DD'] の形で抽出
        regDate = re.search(r'\d+/\d+', date)
        if (regDate == None):
            raise Exception("Invalid Date Format.")
        month_day_list = regDate.group().split('/')
        TERAKOYA_START_TIME = 17
        return datetime(
            year=datetime.now(JST).year,
            month=int(month_day_list[0]),
            day=int(month_day_list[1]),
            hour=TERAKOYA_START_TIME,  # To send a remind mail at an hour before Terakoya starts
            tzinfo=JST
        )

    @staticmethod
    def convert_iso_to_slushdate(iso_date: str):
        return datetime.fromisoformat(iso_date).strftime(f"%m/%d")


if __name__ == "__main__":
    pass
