import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.api.booking import TERAKOYA_TYPE, ARRIVAL_TIME, GRADE, TERAKOYA_EXPERIENCE, STUDY_SUBJECT, STUDY_STYLE, COURSE_CHOICE, HOW_TO_KNOW_TERAKOYA

from functions.utils.dt import DT

name = "I.G"
email = "i.g.freetech2021@gmail.com"
terakoya_type = TERAKOYA_TYPE.HIGH_IKE.value
attendance_date_list = ["3000-01-07", "3000-01-14", "3000-01-21"]  # All dates are Tuesday
arrival_time = ARRIVAL_TIME.AFTER_1800.value
grade = GRADE.OTHER.value
terakoya_experience = TERAKOYA_EXPERIENCE.FIRST_TIME.value
study_subject = STUDY_SUBJECT.EIKEN.value
study_subject_detail = "I'm studying English."
study_style = STUDY_STYLE.CONSULT.value
school_name = "Hogwarts School of Witchcraft and Wizardry"
first_choice_school = "MIT"
course_choice = COURSE_CHOICE.LIBERAL_ARTS.value
future_free = "I want to be a wizard."
like_thing_free = "I like magic.\nAnd I like to play Quidditch."
how_to_know_terakoya = HOW_TO_KNOW_TERAKOYA.LEAFLET.value
remarks = f"Current time is {DT.CURRENT_JST_DATETIME.strftime('%Y-%m-%d %H:%M:%S')}."

book_request_body = {
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
