import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.utils.dt import DT

name = "I.G"
email = "i.g.freetech2021@gmail.com"
terakoya_type = 1
attendance_date_list = ["3000-01-07", "3000-01-14", "3000-01-21"]  # All dates are Tuesday
arrival_time = 0
grade = 13
terakoya_experience = 1
study_subject = 9
study_subject_detail = "I'm studying English."
study_style = 5
school_name = "Hogwarts School of Witchcraft and Wizardry"
first_choice_school = "MIT"
course_choice = 3
future_free = "I want to be a wizard."
like_thing_free = "I like magic.\nAnd I like to play Quidditch."
how_to_know_terakoya = 6
remarks = f"Current time is {DT.CURRENT_JST_DATETIME.strftime('%Y-%m-%d %H:%M:%S')}."

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
