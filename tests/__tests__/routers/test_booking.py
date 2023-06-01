import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.routers import booking
from functions.utils.dt import DT

EXCLUDED_DATES_CSV_FOR_TEST_FKEY = f"api/booking/excluded_dates_for_test.csv"


def test_update_excluded_dates():
    dates = ["2023-06-03", "2023-06-10", DT.CURRENT_JST_ISO_8601_ONLY_DATE]
    booking.update_excluded_dates(dates, EXCLUDED_DATES_CSV_FOR_TEST_FKEY)
    response = booking.fetch_excluded_dates(EXCLUDED_DATES_CSV_FOR_TEST_FKEY)
    assert response["dates"] == dates
