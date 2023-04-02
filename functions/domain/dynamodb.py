import os
import sys
from typing import cast
from datetime import datetime
import hashlib
import boto3
from boto3.dynamodb.conditions import Key, Attr

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.dt import DT

from api.booking import TERAKOYA_TYPE, TERAKOYA_EXPERIENCE, GRADE, ARRIVAL_TIME, STUDY_STYLE, STUDY_SUBJECT, COURSE_CHOICE, HOW_TO_KNOW_TERAKOYA, PLACE

from config.aws_config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, DYNAMO_DB_BOOKING_TABLE


class BookingItem:
    def __init__(
        self,
        date: str,
        email: str,
        terakoya_type: int,
        place: int,
        name: str,
        grade: int,
        arrival_time: int,
        terakoya_experience: int,
        study_subject: int,
        study_subject_detail: str,
        study_style: int,
        school_name: str,
        first_choice_school: str,
        course_choice: int,
        future_free: str,
        like_thing_free: str,
        how_to_know_terakoya: int,
        remarks: str,
        is_reminded: int = 0,
    ) -> None:
        self.date = date
        self.sk = f"#{email}#{terakoya_type}#{place}"
        self.email = email
        self.terakoya_type = terakoya_type
        self.place = place
        self.name = name
        self.grade = grade
        self.arrival_time = arrival_time
        self.terakoya_experience = terakoya_experience
        self.study_subject = study_subject
        self.study_subject_detail = study_subject_detail
        self.study_style = study_style
        self.school_name = school_name
        self.first_choice_school = first_choice_school
        self.course_choice = course_choice
        self.future_free = future_free
        self.like_thing_free = like_thing_free
        self.how_to_know_terakoya = how_to_know_terakoya
        self.remarks = remarks
        self.is_reminded = is_reminded
        self.date_unix_time = DT.convert_iso_to_timestamp(date)


class BookingDynamoDB:
    __table = boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    ).Table(DYNAMO_DB_BOOKING_TABLE)

    @classmethod
    def insert_item(cls, item: BookingItem, timestamp: int = int(datetime.now().timestamp())):
        """
        timestamp: to set the same timestamp between several items
        """
        primary_key = f"#{item.date}{item.sk}"
        cls.__table.put_item(Item={
            "date": item.date,
            "sk": item.sk,
            "email": item.email,
            "terakoya_type": item.terakoya_type,
            "place": item.place,
            "is_reminded": item.is_reminded,
            "name": item.name,
            "grade": item.grade,
            "arrival_time": item.arrival_time,
            "terakoya_experience": item.terakoya_experience,
            "study_subject": item.study_subject,
            "study_subject_detail": item.study_subject_detail,
            "study_style": item.study_style,
            "school_name": item.school_name,
            "first_choice_school": item.first_choice_school,
            "course_choice": item.course_choice,
            "future_free": item.future_free,
            "like_thing_free": item.like_thing_free,
            "how_to_know_terakoya": item.how_to_know_terakoya,
            "remarks": item.remarks,
            "timestamp": timestamp,
            "uid": hashlib.md5(primary_key.encode()).hexdigest(),
            # https://www.blog.danishi.net/2019/08/09/post-2091/
            "date_unix_time": DT.convert_iso_to_timestamp(item.date),
        })

    @classmethod
    def update_is_reminded(cls, sk: str):
        cls.__table.update_item(
            Key={
                "date": DT.CURRENT_JST_ISO_8601_ONLY_DATE,
                "sk": sk
            },
            ConditionExpression="#is_reminded <> :is_reminded_true",
            UpdateExpression="set #is_reminded = :is_reminded_true",
            ExpressionAttributeNames={
                "#is_reminded": "is_reminded"
            },
            ExpressionAttributeValues={
                ":is_reminded_true": 1
            })

    @classmethod
    def get_item_list(cls, target_date: str):
        # PK can only accept the "=" operator
        # https://dynobase.dev/dynamodb-errors/dynamodb-query-key-condition-not-supported/
        # Key condition types
        # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/LegacyConditionalParameters.KeyConditions.html
        items = cls.__table.query(
            KeyConditionExpression=Key("date").eq(target_date),
        ).get("Items", [])
        return items

    @ classmethod
    def get_item_list_for_remind(cls):
        IS_NOT_REMINDED = 0
        # Limit of query
        # https://zoe6120.com/2019/02/20/503/
        items = cls.__table.query(
            KeyConditionExpression=Key("date").eq(
                DT.CURRENT_JST_ISO_8601_ONLY_DATE),
            FilterExpression=Attr("is_reminded").eq(IS_NOT_REMINDED)
        ).get("Items", [])

        booking_item_list = [BookingItem(
            cast(str, item["date"]),  # PK
            cast(str, item["email"]),  # SK
            cast(int, item["terakoya_type"]),  # SK
            cast(int, item["place"]),  # SK
            cast(str, item.get("name", "")),
            cast(int, item.get("grade", GRADE.NULL)),
            cast(int, item.get("arrival_time", ARRIVAL_TIME.NULL)),
            cast(int, item.get("terakoya_experience", TERAKOYA_EXPERIENCE.NULL)),
            cast(int, item.get("study_subject", STUDY_SUBJECT.NULL)),
            cast(str, item.get("study_subject_detail", "")),
            cast(int, item.get("study_style", STUDY_STYLE.NULL)),
            cast(str, item.get("school_name", "")),
            cast(str, item.get("first_choice_school", "")),
            cast(int, item.get("course_choice", COURSE_CHOICE.LIBERAL_ARTS)),
            cast(str, item.get("future_free", "")),
            cast(str, item.get("like_thing_free", "")),
            cast(int, item.get("how_to_know_terakoya", HOW_TO_KNOW_TERAKOYA.NULL)),
            cast(str, item.get("remarks", "")),
            cast(int, item.get("is_reminded", IS_NOT_REMINDED))) for item in items]
        return booking_item_list


if __name__ == "__main__":
    # Test case 1
    date_list = ["2023-01-31", "2023-02-07", "2023-02-14"]
    # date_list = ["2023-02-21", "2023-02-28"]
    test_item_1: BookingItem
    for date in date_list:
        test_item_1 = BookingItem(
            arrival_time=ARRIVAL_TIME.BEFORE_1700.value,
            course_choice=COURSE_CHOICE.TBD.value,
            date=date,
            email="laughingman2045.sac@gmail.com",
            future_free="Future",
            grade=GRADE.HIGH_1.value,
            how_to_know_terakoya=HOW_TO_KNOW_TERAKOYA.INSTAGRAM.value,
            like_thing_free="Like",
            name="Test1",
            place=PLACE.TBD.value,
            remarks="Remarks",
            school_name="School",
            first_choice_school="My First Choice School 1",
            study_subject=STUDY_SUBJECT.AO_ENTRANCE.value,
            study_subject_detail="Study Detail",
            study_style=STUDY_STYLE.CONSULT.value,
            terakoya_experience=TERAKOYA_EXPERIENCE.DONE.value,
            terakoya_type=TERAKOYA_TYPE.HIGH_IKE.value,
        )
        BookingDynamoDB.insert_item(test_item_1)

    # Test case 2
    date_list = ["2023-01-31", "2023-02-28"]
    # date_list = ["2023-02-07", "2023-02-21"]
    test_item_2: BookingItem
    for date in date_list:
        test_item_2 = BookingItem(
            arrival_time=ARRIVAL_TIME.AFTER_1800.value,
            course_choice=COURSE_CHOICE.SCIENCE.value,
            date=date,
            email="coda2045@gmail.com",
            future_free="Future2",
            grade=GRADE.OTHER.value,
            how_to_know_terakoya=HOW_TO_KNOW_TERAKOYA.INTRODUCE.value,
            like_thing_free="Like2",
            name="Test1",
            place=PLACE.CAREER_MOM.value,
            remarks="Remarks2",
            school_name="School2",
            first_choice_school="My First Choice School 2",
            study_subject=STUDY_SUBJECT.ENG.value,
            study_subject_detail="Study Detail2",
            study_style=STUDY_STYLE.TALKING.value,
            terakoya_experience=TERAKOYA_EXPERIENCE.FIRST_TIME.value,
            terakoya_type=TERAKOYA_TYPE.ONLINE_TAMA.value,
        )
        BookingDynamoDB.insert_item(test_item_2)
    # BookingDynamo.update_is_reminded(test_item_2.sk)
    bk_item_list = BookingDynamoDB.get_item_list_for_remind()
    pass
