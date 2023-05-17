import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

# Grouping multiple tests in a class
# https://docs.pytest.org/en/7.1.x/getting-started.html#group-multiple-tests-in-a-class
# https://zenn.dev/ymiz/articles/c25dcddfedd7c3


class TestBookingItem:
    def test_convert_from_request_body(self):
        from functions.models.booking import BookingItem

        request_body = {
            "name": "I.G",
            "email": "i.g.freetech2021@gmail.com",
            "terakoya_type": 1,
            "attendance_date_list": [
                    "2023-05-16"
            ],
            "arrival_time": 1,
            "grade": 2,
            "terakoya_experience": 2,
            "study_subject": 8,
            "study_subject_detail": "AHAHA",
            "study_style": 1,
            "school_name": "",
            "first_choice_school": "",
            "course_choice": 999,
            "future_free": "",
            "like_thing_free": "",
            "how_to_know_terakoya": 999,
            "remarks": "AHAHA"
        }

        booking_item = BookingItem(**request_body)
