import os
import sys
import pytest
from datetime import datetime

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.utils.dt import DT, JST_TZ

MOCK_NOW_DATE = datetime(2045, 5, 8)


@pytest.mark.freeze_time(MOCK_NOW_DATE)  # datetime.now() is mocked to return a fixed value
# https://webbibouroku.com/Blog/Article/pytest-datetime-mock
class TestDT:
    # Define class attributes
    # https://docs.pytest.org/en/7.1.x/getting-started.html#group-multiple-tests-in-a-class
    test_date = "2045-05-08"

    def test_CURRENT_JST_DATETIME(self):
        assert DT.CURRENT_JST_DATETIME == MOCK_NOW_DATE.astimezone(JST_TZ)
        assert DT.CURRENT_JST_DATETIME != MOCK_NOW_DATE  # NG due to timezone
        assert False

    def test_CURRENT_JST_ISO_8601_ONLY_DATE(self):
        assert DT.CURRENT_JST_ISO_8601_ONLY_DATE == self.test_date

    def test_convert_iso_to_slushdate(self):
        # Specify self.prop_name to access class attributes
        assert DT.convert_iso_to_slushdate(self.test_date) == "05/08"
        assert DT.convert_iso_to_slushdate(self.test_date) == "5/8"  # NG due to zero padding

    def test_convert_iso_to_timestamp(self):
        assert DT.convert_iso_to_timestamp(self.test_date) == 2377814400
