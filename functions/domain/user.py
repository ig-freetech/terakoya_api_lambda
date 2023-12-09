import os
import sys
from decimal import Decimal
from fastapi import UploadFile, HTTPException

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import STAGE, S3_TERAKOYA_PUBLIC_BUCKET_NAME
from domain import timeline
from models.user import UserItem, EMPTY_SK
from utils.aws import dynamodb_resource, s3_client
from utils.dt import DT

__table = dynamodb_resource.Table(f"terakoya-{STAGE}-user")


def insert_item(item: UserItem):
    # BaseModel must be converted to dict with .dict() method to add an item to DynamoDB table.
    # https://docs.pydantic.dev/latest/usage/exporting_models/#modeldict
    __table.put_item(Item=item.to_dynamodb_item())


def delete_item(uuid: str, sk: str):
    # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/GettingStarted.DeleteItem.html
    __table.delete_item(Key={
        # Error occurs unless you don't specify both partition key and sort key if the table has both of them.
        # https://confrage.jp/aws-lambdapython3-6%E3%81%8B%E3%82%89dynamodb%E3%81%AE%E3%83%87%E3%83%BC%E3%82%BF%E3%82%92%E5%89%8A%E9%99%A4%E3%81%99%E3%82%8B/
        "uuid": uuid,
        "sk": sk
    })


def fetch_item(uuid: str, sk: str):
    # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
    item = __table.get_item(Key={
        "uuid": uuid,
        "sk": sk
    }).get("Item", {})
    return item


def update_item(item: UserItem):
    # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/GettingStarted.Python.03.html
    __table.update_item(
        Key={
            "uuid": item.uuid,
            "sk": item.sk
        },
        UpdateExpression="""
            set
            #name = :name,
            #nickname = :nickname,
            #school = :school,
            #grade = :grade,
            #course_choice = :course_choice,
            #staff_in_charge = :staff_in_charge,
            #future_path = :future_path,
            #like_thing = :like_thing,
            #how_to_know_terakoya = :how_to_know_terakoya,
            #number_of_attendances = :number_of_attendances,
            #attendance_rate = :attendance_rate,
            #is_admin = :is_admin,
            #updated_at_iso = :updated_at_iso
        """,
        ExpressionAttributeNames={
            "#name": "name",
            "#nickname": "nickname",
            "#school": "school",
            "#grade": "grade",
            "#course_choice": "course_choice",
            "#staff_in_charge": "staff_in_charge",
            "#future_path": "future_path",
            "#like_thing": "like_thing",
            "#how_to_know_terakoya": "how_to_know_terakoya",
            "#number_of_attendances": "number_of_attendances",
            "#attendance_rate": "attendance_rate",
            "#is_admin": "is_admin",
            "#updated_at_iso": "updated_at_iso"
        },
        ExpressionAttributeValues={
            ":name": item.name,
            ":nickname": item.nickname,
            ":school": item.school,
            ":grade": item.grade.value,
            ":course_choice": item.course_choice.value,
            ":staff_in_charge": item.staff_in_charge,
            ":future_path": item.future_path,
            ":like_thing": item.like_thing,
            ":how_to_know_terakoya": item.how_to_know_terakoya.value,
            # Analytics
            ":number_of_attendances": item.number_of_attendances,
            ":attendance_rate": Decimal(str(item.attendance_rate)),
            # Authority
            ":is_admin": item.is_admin.value,
            # Timestamp
            ":updated_at_iso": DT.CURRENT_JST_ISO_8601_DATETIME,
        }
    )


def fetch_profile(uuid: str, sk: str):
    user_item = UserItem(**fetch_item(uuid, sk))
    profile = user_item.to_profile()
    return profile.dict()

def update_profile_img(uuid: str, file: UploadFile):
    fname = file.filename
    if fname is None:
        raise HTTPException(status_code=400, detail="Profile image file name is not specified.")
    
    if S3_TERAKOYA_PUBLIC_BUCKET_NAME is None:
        raise HTTPException(status_code=500, detail="S3_TERAKOYA_BUCKET_NAME is not set.")

    key = f"users/{uuid}/{fname}"
    s3_img_url = f"https://{S3_TERAKOYA_PUBLIC_BUCKET_NAME}.s3.amazonaws.com/{key}"
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/upload_fileobj.html
    s3_client.upload_fileobj(file.file, S3_TERAKOYA_PUBLIC_BUCKET_NAME, key)
    __table.update_item(
        Key={
            "uuid": uuid,
            "sk": EMPTY_SK
        },
        UpdateExpression="""
            set
            #user_profile_img_url = :user_profile_img_url,
            #updated_at_iso = :updated_at_iso
        """,
        ExpressionAttributeNames={
            "#user_profile_img_url": "user_profile_img_url",
            "#updated_at_iso": "updated_at_iso"
        },
        ExpressionAttributeValues={
            ":user_profile_img_url": s3_img_url,
            ":updated_at_iso": DT.CURRENT_JST_ISO_8601_DATETIME,
        }
    )
    timeline.update_user_profile_img(uuid, s3_img_url)