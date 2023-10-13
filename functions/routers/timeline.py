import os
import sys
from typing import Optional
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from domain.timeline import fetch_timeline_list, fetch_user_timeline_list, post_timeline_item, post_comment_item, put_reaction_item_to_post, put_reaction_item_to_comment, fetch_comment_list, FetchListResponseBody
from models.timeline import PostItem, CommentItem, Reaction
from utils.process import hub_lambda_handler_wrapper_with_rtn_value, hub_lambda_handler_wrapper

timeline_router = APIRouter()

# https://fastapi.tiangolo.com/ja/tutorial/query-params/


@timeline_router.get("/list", response_model=FetchListResponseBody[PostItem])
def get_timeline_list(request: Request, response: Response, last_evaluated_key: Optional[str] = None):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: fetch_timeline_list(last_evaluated_key=last_evaluated_key),
        request=request
    )


@timeline_router.get("/list/{uuid}", response_model=FetchListResponseBody[PostItem])
def get_timeline_list_by_uuid(uuid: str, request: Request, response: Response, last_evaluated_key: Optional[str] = None):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: fetch_user_timeline_list(
            uuid=uuid,
            last_evaluated_key=last_evaluated_key
        ),
        request=request
    )


@timeline_router.post("")
def post_timeline(request_body: PostItem, request: Request, response: Response):
    return hub_lambda_handler_wrapper(
        lambda: post_timeline_item(post=request_body),
        request=request,
        request_data=request_body.dict()
    )


@timeline_router.get("/{post_id}/comment/list", response_model=FetchListResponseBody[CommentItem])
def get_comment_list(post_id: str, request: Request, response: Response, last_evaluated_key: Optional[str] = None):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: fetch_comment_list(
            post_id=post_id,
            last_evaluated_key=last_evaluated_key
        ),
        request=request
    )


@timeline_router.post("/{post_id}/comment")
def post_comment(post_id: str, request_body: CommentItem, request: Request, response: Response):
    return hub_lambda_handler_wrapper(
        lambda: post_comment_item(
            post_id=post_id,
            comment=request_body
        ),
        request=request,
        request_data=request_body.dict()
    )


class PutReactionToPostReqBody(BaseModel):
    uuid: str
    reaction: Reaction


@timeline_router.put("/{post_id}/reaction")
def put_reaction_to_post(post_id: str, request_body: PutReactionToPostReqBody, request: Request, response: Response):
    return hub_lambda_handler_wrapper(
        lambda: put_reaction_item_to_post(
            uuid=request_body.uuid,
            post_id=post_id,
            reaction=request_body.reaction
        ),
        request=request,
        request_data=request_body.dict()
    )


@timeline_router.put("/{post_id}/comment/{comment_id}/reaction")
def put_reaction_to_comment(post_id: str, comment_id: str, request_body: Reaction, request: Request, response: Response):
    return hub_lambda_handler_wrapper(
        lambda: put_reaction_item_to_comment(
            post_id=post_id,
            comment_id=comment_id,
            reaction=request_body
        ),
        request=request,
        request_data=request_body.dict()
    )
