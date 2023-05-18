import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.api.booking import GRADE

DATE1 = "2045-05-08"
DATE2 = "2045-05-15"

NAME = "I.G"
EMAIL = "i.g.freetech2021@gmail.com",
TERAKOYA_TYPE = 1,
ATTENDANCE_DATE_LIST = [DATE1, DATE2],
ARRIVAL_TIME = 1,
GRADE = GRADE.HIGH_2.value,

REQUEST_BODY = {
    "name": NAME,
    "email": EMAIL,
    "terakoya_type": TERAKOYA_TYPE,
    "attendance_date_list": ATTENDANCE_DATE_LIST,
    "arrival_time": ARRIVAL_TIME,
    "grade": GRADE,
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