import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

name = "Test"
email = "i.g.freetech2021@gmail.com"
terakoya_type = 1
attendance_date_list = ["3000-01-07", "3000-01-14", "3000-01-21"]  # All dates are Tuesday
arrival_time = 0
# Boundary value test
# https://www.veriserve.co.jp/gihoz/boundary.html
# https://qiita.com/softest/items/648d8bb4021cd1256b02
grade = 13
terakoya_experience = 1
study_subject = 9
study_subject_detail = "Test"
study_style = 5
school_name = "Test"
first_choice_school = "MIT"
course_choice = 3
future_free = "This is test.\nThis is pytest."
like_thing_free = "This is test.\nThis is pytest."
how_to_know_terakoya = 6
remarks = ""

book_request_body_json = {
    "name": name,
    "email": email,
    "terakoya_type": terakoya_type,
    "attendance_date_list": attendance_date_list,
    "arrival_time": arrival_time,
    "grade": grade,
    "terakoya_experience": terakoya_experience,
    "study_subject": study_subject,
    "study_subject_detail": study_subject_detail,
    "study_style": study_style,
    "school_name": school_name,
    "first_choice_school": first_choice_school,
    "course_choice": course_choice,
    "future_free": future_free,
    "like_thing_free": like_thing_free,
    "how_to_know_terakoya": how_to_know_terakoya,
    "remarks": remarks
}
