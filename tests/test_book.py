import os
import sys
import json
import requests

from samples.booking import book_request_body_json

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_DEFAULT_REGION, GATEWAY_ID_DEV

from functions.book import BookingRequest
from functions.models.booking import TERAKOYA_TYPE_TO_PLACE_MAP, BookingItem
from functions.domain.booking import generate_sk, BookingTable
from tests.samples.booking import book_request_body_json, attendance_date_list, name, email, terakoya_type, arrival_time, grade, terakoya_experience, study_subject, study_subject_detail, study_style, school_name, first_choice_school, course_choice, future_free, like_thing_free, how_to_know_terakoya, remarks

# Grouping multiple tests in a class
# https://docs.pytest.org/en/7.1.x/getting-started.html#group-multiple-tests-in-a-class
# https://zenn.dev/ymiz/articles/c25dcddfedd7c3


def test_lambda():
    base_url = f"https://{GATEWAY_ID_DEV}.execute-api.{AWS_DEFAULT_REGION}.amazonaws.com"
    # Unless specifying Content-Type, the request body is not recognized as JSON and decoded as a string incorrectly in Lambda
    response = requests.post(f"{base_url}/book", headers={'Content-Type': 'application/json'}, data=json.dumps({
        **book_request_body_json, "attendance_date_list": ["4000-01-04"], "remarks": "pytest_book_via_api_gateway"},
    ))
    print(response)
    response_body = response.json()
    print(response_body)
    assert response.status_code == 200
    assert response_body.get("status_code") == 200


def test_func():
    booking_request = BookingRequest({**book_request_body_json, "remarks": "pytest_book_via_func"})
    # List comprehension is better to do the same thing as Array.map(obj => obj.prop) in JavaScript rather than using map(lambda x: x.prop, list)
    # https://blog.utgw.net/entry/2017/03/09/154314
    date_list = [bk_item.date for bk_item in booking_request.booking_item_list]
    assert attendance_date_list[0] in date_list
    # assert date1 in map(lambda bk_item: bk_item.date, booking.booking_item_list)
    assert booking_request.booking_item_list[0].name == name
    assert booking_request.booking_item_list[0].email == email
    assert booking_request.booking_item_list[0].terakoya_type == terakoya_type
    assert booking_request.booking_item_list[0].arrival_time == arrival_time
    assert booking_request.booking_item_list[0].grade == grade
    assert booking_request.booking_item_list[0].terakoya_experience == terakoya_experience
    assert booking_request.booking_item_list[0].study_subject == study_subject
    assert booking_request.booking_item_list[0].study_subject_detail == study_subject_detail
    assert booking_request.booking_item_list[0].study_style == study_style
    assert booking_request.booking_item_list[0].school_name == school_name
    assert booking_request.booking_item_list[0].first_choice_school == first_choice_school
    assert booking_request.booking_item_list[0].course_choice == course_choice
    assert booking_request.booking_item_list[0].future_free == future_free
    assert booking_request.booking_item_list[0].like_thing_free == like_thing_free
    assert booking_request.booking_item_list[0].how_to_know_terakoya == how_to_know_terakoya
    assert booking_request.booking_item_list[0].remarks == remarks
    assert booking_request.booking_item_list[0].place == TERAKOYA_TYPE_TO_PLACE_MAP[terakoya_type]
    assert booking_request.booking_item_list[0].sk == generate_sk(email, terakoya_type)
    assert attendance_date_list[1] in date_list
    assert attendance_date_list[2] in date_list
    booking_request.book()
    bk_item = BookingItem(**BookingTable.get_item(date_list[0], email, terakoya_type))
    assert bk_item.timestamp == booking_request.booking_item_list[0].timestamp
    assert bk_item.uid == booking_request.booking_item_list[0].uid
