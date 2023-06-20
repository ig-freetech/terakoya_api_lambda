import os
import sys
import boto3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE
from models.user import UserItem

__table = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
).Table(f"terakoya-{STAGE}-user")


def insert_item(item: UserItem):
    # BaseModel must be converted to dict with .dict() method to add an item to DynamoDB table.
    # https://docs.pydantic.dev/latest/usage/exporting_models/#modeldict
    __table.put_item(Item=item.dict())


def delete_item(uuid: str, sk: str):
    # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/GettingStarted.DeleteItem.html
    __table.delete_item(Key={
        # Error occurs unless you don't specify both partition key and sort key if the table has both of them.
        # https://confrage.jp/aws-lambdapython3-6%E3%81%8B%E3%82%89dynamodb%E3%81%AE%E3%83%87%E3%83%BC%E3%82%BF%E3%82%92%E5%89%8A%E9%99%A4%E3%81%99%E3%82%8B/
        "uuid": uuid,
        "sk": sk
    })
