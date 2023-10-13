import os
import sys
from typing import List, Optional, TypeVar
import boto3
from fastapi import HTTPException, status
from pydantic.generics import GenericModel, Generic, BaseModel

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE
from models.timeline import PK_FOR_ALL_POST_GSI, PostItem, CommentItem, Reaction

DYNAMO_DB_RESOURCE = boto3.resource(
    "dynamodb",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)
__post_table = DYNAMO_DB_RESOURCE.Table(f"terakoya-{STAGE}-timeline-post")
__comment_table = DYNAMO_DB_RESOURCE.Table(f"terakoya-{STAGE}-timeline-comment")

T = TypeVar("T", bound=BaseModel)


class FetchListResponseBody(GenericModel, Generic[T]):
    items: List[T]
    last_evaluated_key: Optional[str]


def fetch_timeline_list(last_evaluated_key: Optional[str] = None):
    query_params = {
        "IndexName": f"terakoya-{STAGE}-timeline-post-all",
        "KeyConditionExpression": 'pk_for_all_post_gsi = :value',
        "ExpressionAttributeValues": {
            ':value': PK_FOR_ALL_POST_GSI
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


def fetch_user_timeline_list(uuid: str, last_evaluated_key: Optional[str] = None):
    query_params = {
        "KeyConditionExpression": 'uuid = :value',
        "ExpressionAttributeValues": {
            ':value': uuid
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


def post_timeline_item(post: PostItem):
    __post_table.put_item(Item=post.dict())


def fetch_comment_list(post_id: str, last_evaluated_key: Optional[str] = None):
    query_params = {
        "KeyConditionExpression": 'post_id = :value',
        "ExpressionAttributeValues": {
            ':value': post_id
        },
        "Limit": 20,
        # The result of query() is sorted by sort key in ascending order by default.
        # But ScanIndexForward=False makes it descending order. If sort key is timestamp, it means latest first.
        # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/Query.html#Query.KeyConditionExpressions
        "ScanIndexForward": False,
    }

    if last_evaluated_key:
        query_params["ExclusiveStartKey"] = last_evaluated_key

    response = __comment_table.query(**query_params)

    return {
        "items": response.get("Items", []),
        "last_evaluated_key": response.get("LastEvaluatedKey", None)
    }


def post_comment_item(post_id: str, comment: CommentItem):
    __comment_table.put_item(Item=comment.dict())
    __post_table.update_item(
        Key={
            "post_id": post_id
        },
        UpdateExpression="ADD comment_count :val",
        ExpressionAttributeValues={
            ":val": 1
        }
    )


def put_reaction_item_to_post(uuid: str, post_id: str, reaction: Reaction):
    print(f"reaction: {reaction}")

    post_item = __post_table.get_item(Key={
        "uuid": uuid,
        "post_id": post_id
    }).get("Item", {})
    pi = PostItem(**post_item)

    new_reactions = []
    if reaction.uuid in [r.uuid for r in pi.reactions]:
        if reaction.type in [r.type for r in pi.reactions]:
            print("Already reacted to this post with same reaction type. So removed reaction.")
            new_reactions = [r for r in pi.reactions if r.uuid != reaction.uuid and r.type != reaction.type]
        else:
            print("Already reacted to this post with different reaction type.")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="この投稿には既に別のリアクションがされています。")
    else:
        print("Not reacted to this post yet. So added reaction.")
        new_reactions = pi.reactions + [reaction]

    __post_table.update_item(
        Key={
            "post_id": post_id
        },
        UpdateExpression="SET reactions = :val",
        ExpressionAttributeValues={
            ":val": new_reactions
        }
    )


def put_reaction_item_to_comment(post_id: str, comment_id: str, reaction: Reaction):
    print(f"reaction: {reaction}")

    comment_item = __comment_table.get_item(Key={
        "post_id": post_id,
        "comment_id": comment_id
    }).get("Item", {})
    ci = CommentItem(**comment_item)

    new_reactions = []
    if reaction.uuid in [r.uuid for r in ci.reactions]:
        if reaction.type in [r.type for r in ci.reactions]:
            print("Already reacted to this comment with same reaction type. So removed reaction.")
            new_reactions = [r for r in ci.reactions if r.uuid != reaction.uuid and r.type != reaction.type]
        else:
            print("Already reacted to this comment with different reaction type.")
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="この投稿には既に別のリアクションがされています。")
    else:
        print("Not reacted to this comment yet. So added reaction.")
        new_reactions = ci.reactions + [reaction]

    __comment_table.update_item(
        Key={
            "post_id": post_id,
            "comment_id": comment_id
        },
        UpdateExpression="SET reactions = :val",
        ExpressionAttributeValues={
            ":val": new_reactions
        }
    )


def update_user_info(uuid: str, sk: str, user_name: str, user_profile_img_url: str):
    # TODO: query() -> update_item() in parallel for each items
    pass
