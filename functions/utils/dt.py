import os
import sys
from datetime import datetime, timezone, timedelta

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from utils.subclass import classproperty

TIME_DIFFERENCE_UTC_JAPAN_HOUR = 9
JST_TZ = timezone(timedelta(hours=TIME_DIFFERENCE_UTC_JAPAN_HOUR), "JST")

ISO_DATE_FORMAT = "%Y-%m-%d"
ISO_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class DT:
    @classproperty
    @classmethod
    def CURRENT_JST_DATETIME(cls) -> datetime:
        return datetime.now(JST_TZ)

    @classproperty
    @classmethod
    def CURRENT_JST_ISO_8601_ONLY_DATE(cls) -> str:
        return cls.CURRENT_JST_DATETIME.strftime(ISO_DATE_FORMAT)

    @classproperty
    @classmethod
    def CURRENT_JST_ISO_8601_DATETIME(cls) -> str:
        return cls.CURRENT_JST_DATETIME.strftime(ISO_DATETIME_FORMAT)

    @staticmethod
    def convert_iso_to_slushdate(iso_date: str):
        return datetime.fromisoformat(iso_date).strftime(f"%m/%d")

    @staticmethod
    def convert_iso_to_timestamp(iso_date: str) -> int:
        # https://kokufu.blogspot.com/2018/12/python-datetime-unix-time.html
        return int(datetime.strptime(iso_date, ISO_DATE_FORMAT).timestamp())
