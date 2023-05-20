import os
import sys
import json
import boto3

from samples.booking import book_request_body_json

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE

from functions.book import BookingRequest
from functions.models.booking import TERAKOYA_TYPE_TO_PLACE_MAP
from functions.domain.booking import generate_sk, BookingTable
from tests.samples.booking import book_request_body_json, attendance_date_list, name, email, terakoya_type, arrival_time, grade, terakoya_experience, study_subject, study_subject_detail, study_style, school_name, first_choice_school, course_choice, future_free, like_thing_free, how_to_know_terakoya, remarks

# Grouping multiple tests in a class
# https://docs.pytest.org/en/7.1.x/getting-started.html#group-multiple-tests-in-a-class
# https://zenn.dev/ymiz/articles/c25dcddfedd7c3


def test_lambda():
    client = boto3.client('lambda', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)
    response = client.invoke(
        FunctionName=f'terakoya-booking-renewal-dev-book',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "body": book_request_body_json
        })
    )
    print(response)
    print(response['Payload'])
    assert response['StatusCode'] == 200
    assert response['FunctionError'] is None


def test_func():
    """NOTE: Maybe this test case is unnecessary because it's redundant"""
    booking_request = BookingRequest(book_request_body_json)
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
    BookingTable.get_item(date_list[0], email, terakoya_type)
