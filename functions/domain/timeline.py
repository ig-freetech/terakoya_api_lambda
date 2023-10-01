import os
import sys
from typing import Optional
import boto3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE
from utils.dt import DT
from models.timeline import PostItem, CommentItem

DYNAMO_DB_RESOURCE = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)
__post_table = DYNAMO_DB_RESOURCE.Table(f"terakoya-{STAGE}-timeline-posts")
__comment_table = DYNAMO_DB_RESOURCE.Table(f"terakoya-{STAGE}-timeline-comments")

ALL_GSI_PK = "all_posts"


def fetch_timeline(last_evaluated_key: Optional[str] = None):
    query_params = {
        "IndexName": f"terakoya-{STAGE}-timeline-posts-all",
        "KeyConditionExpression": 'all_pk = :value',
        "ExpressionAttributeValues": {
            ':value': ALL_GSI_PK
        },
        "Limit": 20,
        # The result of query() is sorted by sort key in ascending order by default.
        # But ScanIndexForward=False makes it descending order. If sort key is timestamp, it means latest first.
        # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/Query.html#Query.KeyConditionExpressions
        "ScanIndexForward": False,
    }

    if last_evaluated_key:
        query_params["ExclusiveStartKey"] = last_evaluated_key

    response = __post_table.query(**query_params)

    return {
        "items": response.get("Items", []),
        "last_evaluated_key": response.get("LastEvaluatedKey", None)
    }


def post_timeline(post: PostItem):
    __post_table.put_item(Item=post.dict())


def update_user_info(uuid: str, sk: str, user_name: str, user_profile_img_url: str):
    # TODO: query() -> update_item() in parallel for each items
    pass
