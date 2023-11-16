import os
import sys
from typing import List, Optional, TypeVar
from fastapi import HTTPException, status
from pydantic.generics import GenericModel, Generic, BaseModel

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import STAGE
from models.timeline import PK_FOR_ALL_POST_GSI, PostItem, CommentItem, Reaction
from utils.aws import dynamodb_resource

__post_table = dynamodb_resource.Table(f"terakoya-{STAGE}-timeline-post")
__comment_table = dynamodb_resource.Table(f"terakoya-{STAGE}-timeline-comment")

def post_timeline_item(post: PostItem):
    __post_table.put_item(Item=post.dict())
    return {"post_id": post.post_id}

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

    return {"comment_id": comment.comment_id}


def delete_logical_timeline_item(post_id: str):
    __post_table.update_item(Key={
        "post_id": post_id
    },
        UpdateExpression="set is_deleted = :is_deleted_true",
        ExpressionAttributeValues={
        ":is_deleted_true": 1
    })

def delete_logical_comment_item(post_id: str, comment_id: str):
    __comment_table.update_item(Key={
        "comment_id": comment_id
    },
        UpdateExpression="set is_deleted = :is_deleted_true",
        ExpressionAttributeValues={
        ":is_deleted_true": 1
    })
    __post_table.update_item(
        Key={
            "post_id": post_id
        },
        UpdateExpression="ADD comment_count :val",
        ExpressionAttributeValues={
            ":val": -1
        }
    )


def put_reaction_to_timeline_item(post_id: str, reaction: Reaction):
    print(f"reaction: {reaction}")

    post_item = __post_table.get_item(Key={
        "post_id": post_id
    }).get("Item", {})
    pi = PostItem(**post_item)

    same_user_reactions = [r for r in pi.reactions if r.uuid == reaction.uuid]

    new_reactions = []
    if len(same_user_reactions) == 0:
        print("Not reacted to this post yet. So added reaction.")
        new_reactions = pi.reactions + [reaction]
    elif len(same_user_reactions) == 1:
        existing_reaction = same_user_reactions[0]
        if reaction.type == existing_reaction.type:
            print("Already reacted to the post with the same reaction type. So removed reaction.")
            new_reactions = [r for r in pi.reactions if r.uuid != reaction.uuid]
        else:
            print("Already reacted to the post with the different reaction type. So updated reaction.")
            # raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="この投稿には既に別のリアクションがされています。")
            new_reactions = [r for r in pi.reactions if r.uuid != reaction.uuid] + [reaction]

    __post_table.update_item(
        Key={
            "post_id": post_id
        },
        UpdateExpression="SET reactions = :val",
        ExpressionAttributeValues={
            ":val": [r.dict() for r in new_reactions]
        }
    )


def put_reaction_to_comment_item(comment_id: str, reaction: Reaction):
    print(f"reaction: {reaction}")

    comment_item = __comment_table.get_item(Key={
        "comment_id": comment_id
    }).get("Item", {})
    ci = CommentItem(**comment_item)

    same_user_reactions = [r for r in ci.reactions if r.uuid == reaction.uuid]

    new_reactions = []
    if len(same_user_reactions) == 0:
        print("Not reacted to this comment yet. So added reaction.")
        new_reactions = ci.reactions + [reaction]
    elif len(same_user_reactions) == 1:
        existing_reaction = same_user_reactions[0]
        if reaction.type == existing_reaction.type:
            print("Already reacted to this comment with same reaction type. So removed reaction.")
            new_reactions = [r for r in ci.reactions if r.uuid != reaction.uuid]
        else:
            print("Already reacted to this comment with different reaction type.")
            # raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="この投稿には既に別のリアクションがされています。")
            new_reactions = [r for r in ci.reactions if r.uuid != reaction.uuid] + [reaction]

    __comment_table.update_item(
        Key={
            "comment_id": comment_id
        },
        UpdateExpression="SET reactions = :val",
        ExpressionAttributeValues={
            ":val": [r.dict() for r in new_reactions]
        }
    )

T = TypeVar("T", bound=BaseModel)
class FetchListResponseBody(GenericModel, Generic[T]):
    items: List[T]
    last_evaluated_id: Optional[str]
    count: Optional[int]

def fetch_timeline_list(last_post_id: Optional[str] = None):
    query_params = {
        "IndexName": f"terakoya-{STAGE}-timeline-post-all",
        "KeyConditionExpression": 'pk_for_all_post_gsi = :value',
        # Filtering with is_deleted = 0 is not allowed because it is not a part of the partition key.
        # "KeyConditionExpression": 'pk_for_all_post_gsi = :value and is_deleted = :is_deleted_false',
        "ExpressionAttributeValues": {
            ':value': PK_FOR_ALL_POST_GSI
        },
        "Limit": 20,
        # The result of query() is sorted by sort key in ascending order by default.
        # But ScanIndexForward=False makes it descending order. If sort key is timestamp, it means latest first.
        # https://docs.aws.amazon.com/ja_jp/amazondynamodb/latest/developerguide/Query.html#Query.KeyConditionExpressions
        "ScanIndexForward": False,
    }

    if last_post_id:
        query_params["ExclusiveStartKey"] = {
            "pk_for_all_post_gsi": PK_FOR_ALL_POST_GSI,
            "post_id": last_post_id
        }

    response = __post_table.query(**query_params)
    IS_NOT_DELETED = 0
    active_posts = [p for p in response.get("Items", []) if p.get("is_deleted", IS_NOT_DELETED) == IS_NOT_DELETED]

    last_evaluated_key = response.get("LastEvaluatedKey", None)
    last_post_id = last_evaluated_key.get("post_id", None) if last_evaluated_key else None

    return FetchListResponseBody[PostItem](
        items=active_posts,
        last_evaluated_id=last_post_id,
        count=response.get("Count", None)
    ).dict()


def fetch_timeline_list_by_user(uuid: str, last_post_id: Optional[str] = None):
    query_params = {
        "IndexName": f"terakoya-{STAGE}-timeline-post-by-user",
        "KeyConditionExpression": '#uuid = :value',
        # "uuid" is a reserved keyword in DynamoDB. So you need to use ExpressionAttributeNames.
        # https://dev.classmethod.jp/articles/dynamodb_handling_reserved_keyword/
        "ExpressionAttributeNames": {
            "#uuid": "uuid"
        },
        "ExpressionAttributeValues": {
            ':value': uuid
        },
        "Limit": 20,
        "ScanIndexForward": False,
    }

    if last_post_id:
        query_params["ExclusiveStartKey"] = {
            "uuid": uuid,
            "post_id": last_post_id
        }

    response = __post_table.query(**query_params)
    IS_NOT_DELETED = 0
    active_posts = [p for p in response.get("Items", []) if p.get("is_deleted", IS_NOT_DELETED) == IS_NOT_DELETED]

    last_evaluated_key = response.get("LastEvaluatedKey", None)
    last_post_id = last_evaluated_key.get("post_id", None) if last_evaluated_key else None

    return FetchListResponseBody[PostItem](
        items=active_posts,
        last_evaluated_id=last_post_id,
        count=response.get("Count", None)
    ).dict()

def fetch_comment_list(post_id: str, last_comment_id: Optional[str] = None):
    query_params = {
        "IndexName": f"terakoya-{STAGE}-timeline-comment-for-post",
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

    if last_comment_id:
        query_params["ExclusiveStartKey"] = {
            "comment_id": last_comment_id
        }

    response = __comment_table.query(**query_params)

    last_evaluated_key = response.get("LastEvaluatedKey", None)
    last_comment_id = last_evaluated_key.get("comment_id", None) if last_evaluated_key else None

    return FetchListResponseBody[CommentItem](
        items=response.get("Items", []),
        last_evaluated_id=last_comment_id,
        count=response.get("Count", None)
    ).dict() 


def fetch_timeline_item(post_id: str):
    response = __post_table.get_item(Key={
        "post_id": post_id
    })
    timeline_item = response.get("Item", None)

    if not timeline_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"指定された投稿は存在しません。\npost_id: {post_id}")
    
    return dict(timeline_item)

def fetch_comment_item(comment_id: str):
    """Only for testing"""
    response = __comment_table.get_item(Key={
        "comment_id": comment_id
    })
    comment_item = response.get("Item", None)

    if not comment_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"指定されたコメントは存在しません。\ncomment_id: {comment_id}")
    
    return dict(comment_item)

def update_user_info(uuid: str, user_name: str, user_profile_img_url: str):
    posts_response = __post_table.query(
        IndexName=f"terakoya-{STAGE}-timeline-post-by-user",
        KeyConditionExpression='uuid = :value',
        ExpressionAttributeValues={
            ':value': uuid
        }
    )
    posts = posts_response.get("Items", [])
    for p in posts:
        __post_table.update_item(
            Key={
                "post_id": p.get("post_id")
            },
            UpdateExpression="SET user_name = :user_name, user_profile_img_url = :user_profile_img_url",
            ExpressionAttributeValues={
                ":user_name": user_name,
                ":user_profile_img_url": user_profile_img_url
            }
        )

    comments_response = __comment_table.query(
        IndexName=f"terakoya-{STAGE}-timeline-comment-by-user",
        KeyConditionExpression='uuid = :value',
        ExpressionAttributeValues={
            ':value': uuid
        }
    )
    comments = comments_response.get("Items", [])
    for c in comments:
        __comment_table.update_item(
            Key={
                "comment_id": c.get("comment_id")
            },
            UpdateExpression="SET user_name = :user_name, user_profile_img_url = :user_profile_img_url",
            ExpressionAttributeValues={
                ":user_name": user_name,
                ":user_profile_img_url": user_profile_img_url
            }
        )

def delete_timeline_item(post_id: str):
    """Only for testing"""
    __post_table.delete_item(Key={
        "post_id": post_id
    })

# def get_timeline_item_count():
#     response = __post_table.scan(
#         Select='COUNT'
#     )
#     return response.get("Count", None)

# def get_timeline_item_count_by_user(uuid: str):
#     response = __post_table.query(
#         IndexName=f"terakoya-{STAGE}-timeline-post-by-user",
#         KeyConditionExpression='uuid = :value',
#         ExpressionAttributeValues={
#             ':value': uuid
#         },
#         Select='COUNT'
#     )
#     return response.get("Count", None)

# def get_comment_item_count():
#     response = __comment_table.scan(
#         Select='COUNT'
#     )
#     return response.get("Count", None)