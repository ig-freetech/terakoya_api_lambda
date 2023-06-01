import os
import sys
import datetime

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.routers import booking
from functions.utils.dt import DT, ISO_DATE_FORMAT

EXCLUDED_DATES_CSV_FOR_TEST_FKEY = f"api/booking/excluded_dates_for_test.csv"


def test_update_excluded_dates():
    # Add days to datetime object by datetime + timedelta(days={days})
    # https://pg-chain.com/python-datetime-timedelta
    iso_one_week_later = (DT.CURRENT_JST_DATETIME + datetime.timedelta(days=7)).strftime(ISO_DATE_FORMAT)
    iso_two_week_later = (DT.CURRENT_JST_DATETIME + datetime.timedelta(days=14)).strftime(ISO_DATE_FORMAT)
    dates = [DT.CURRENT_JST_ISO_8601_ONLY_DATE, iso_one_week_later, iso_two_week_later]
    booking.update_excluded_dates(dates, EXCLUDED_DATES_CSV_FOR_TEST_FKEY)
    response = booking.fetch_excluded_dates(EXCLUDED_DATES_CSV_FOR_TEST_FKEY)
    assert response["dates"] == dates
