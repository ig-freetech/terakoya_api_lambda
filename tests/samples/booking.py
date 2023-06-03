import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.models.booking import TERAKOYA_TYPE, ARRIVAL_TIME, GRADE, TERAKOYA_EXPERIENCE, STUDY_SUBJECT, STUDY_STYLE, COURSE_CHOICE, HOW_TO_KNOW_TERAKOYA, PLACE, REMIND_STATUS

email = "i.g.freetech2021@gmail.com"
terakoya_type_value = TERAKOYA_TYPE.HIGH_IKE.value
attendance_date_list = ["3000-01-07", "3000-01-14", "3000-01-21"]  # All dates are Tuesday

book_request_body_json = {
    "name": "Test",
    "email": email,
    "terakoya_type": terakoya_type_value,
    "attendance_date_list": attendance_date_list,
    "arrival_time": ARRIVAL_TIME.AFTER_1800.value,
    # Boundary value test
    # https://www.veriserve.co.jp/gihoz/boundary.html
    # https://qiita.com/softest/items/648d8bb4021cd1256b02
    "grade": GRADE.JUNIOR_HIGH_SCHOOL_3.value,
    "terakoya_experience": TERAKOYA_EXPERIENCE.DONE.value,
    "study_subject": STUDY_SUBJECT.EIKEN.value,
    "study_subject_detail": "Test",
    "study_style": STUDY_STYLE.CONSULT.value,
    "school_name": "Test",
    "first_choice_school": "Test",
    "course_choice": COURSE_CHOICE.SCIENCE.value,
    "future_free": "This is test.\nThis is pytest.",
    "like_thing_free": "This is test.\nThis is pytest.",
    "how_to_know_terakoya": HOW_TO_KNOW_TERAKOYA.POSTER.value,
    "remarks": "This is test.\nThis is pytest."
}

booking_item_json = {
    "date": "2045-05-08",
    "sk": f"#{email}#{terakoya_type_value}",
    "email": email,
    "terakoya_type": terakoya_type_value,
    "name": "Test",
    "grade": GRADE.OTHER.value,
    "arrival_time": ARRIVAL_TIME.BETWEEN_1730_1800.value,
    "terakoya_experience": TERAKOYA_EXPERIENCE.FIRST_TIME.value,
    "study_subject": STUDY_SUBJECT.OTHER.value,
    "study_subject_detail": "Test",
    "study_style": STUDY_STYLE.OTHER.value,
    "school_name": "Test",
    "first_choice_school": "Test",
    "course_choice": COURSE_CHOICE.NULL.value,
    "future_free": "This is test.\nThis is pytest.",
    "like_thing_free": "This is test.\nThis is pytest.",
    "how_to_know_terakoya": HOW_TO_KNOW_TERAKOYA.NULL.value,
    "remarks": "This is test.\nThis is pytest.",
}
