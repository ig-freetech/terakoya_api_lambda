import os
import sys
import boto3
from boto3.dynamodb.conditions import Key, Attr

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from utils.dt import DT
from models.booking import REMIND_STATUS, BookingItem, TERAKOYA_TYPE, PLACE
from conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE

BOOKING_TABLE_NAME = f"terakoya-{STAGE}-booking"


def generate_sk(email: str, terakoya_type: TERAKOYA_TYPE) -> str:
    return f"#{email}#{terakoya_type.value}"


class BookingTable:
    __table = boto3.resource(
        "dynamodb",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_DEFAULT_REGION
    ).Table(BOOKING_TABLE_NAME)

    @classmethod
    def insert_item(cls, item: BookingItem):
        # BaseModel.dict() returns a dict with camelCase keys.
        # https://docs.pydantic.dev/latest/usage/exporting_models/#modeldict
        cls.__table.put_item(Item=item.to_dict())  # to_dict() converts Enum to value

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
                ":is_reminded_true": REMIND_STATUS.SENT.value
            })

    @classmethod
    def update_place(cls, date: str, sk: str, place: PLACE):
        cls.__table.update_item(
            Key={
                "date": date,
                "sk": sk
            },
            UpdateExpression="set #place = :new_place",
            ExpressionAttributeNames={
                "#place": "place"
            },
            ExpressionAttributeValues={
                ":new_place": place.value
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

    @classmethod
    def get_item(cls, target_date: str, email: str, terakoya_type: TERAKOYA_TYPE):
        item = cls.__table.get_item(
            Key={
                "date": target_date,
                "sk": generate_sk(email, terakoya_type)
            }
        ).get("Item", {})
        return item

    @classmethod
    def get_item_list_for_remind(cls):
        # Max limit to be able to get items by a query at once is 1MB
        # https://zoe6120.com/2019/02/20/503/
        items = cls.__table.query(
            KeyConditionExpression=Key("date").eq(
                DT.CURRENT_JST_ISO_8601_ONLY_DATE),
            FilterExpression=Attr("is_reminded").eq(REMIND_STATUS.NOT_SENT.value)
        ).get("Items", [])
        booking_item_list = [BookingItem(**item) for item in items]
        return booking_item_list
