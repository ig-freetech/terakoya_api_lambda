import os
import sys
from typing import Any, Dict, Optional
from fastapi import APIRouter, Request, Response, Depends, Query

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from domain import timeline
from functions.domain.authentication import authenticate_user
from models.timeline import PostItem, CommentItem, Reaction
from utils.process import hub_lambda_handler_wrapper_with_rtn_value, hub_lambda_handler_wrapper


timeline_router = APIRouter()

# https://fastapi.tiangolo.com/ja/tutorial/query-params/


@timeline_router.post("")
def post_timeline(
        request_body: PostItem,
        request: Request,
        response: Response,
        _: Dict[str, Any] = Depends(authenticate_user)):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: timeline.post_timeline_item(post=request_body),
        request=request,
        request_data=request_body.dict()
    )


@timeline_router.post("/{post_id}/comment")
def post_comment(
        post_id: str,
        request_body: CommentItem,
        request: Request,
        response: Response,
        _: Dict[str, Any] = Depends(authenticate_user)):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: timeline.post_comment_item(
            post_id=post_id,
            comment=request_body
        ),
        request=request,
        request_data=request_body.dict()
    )


@timeline_router.put("/{post_id}/reaction")
def put_reaction_to_post(
        post_id: str,
        request_body: Reaction,
        request: Request,
        response: Response,
        _: Dict[str, Any] = Depends(authenticate_user)):
    return hub_lambda_handler_wrapper(
        lambda: timeline.put_reaction_to_timeline_item(
            post_id=post_id,
            reaction=request_body
        ),
        request=request,
        request_data=request_body.dict()
    )


@timeline_router.put("/comment/{comment_id}/reaction")
def put_reaction_to_comment(
        comment_id: str,
        request_body: Reaction,
        request: Request,
        response: Response,
        _: Dict[str, Any] = Depends(authenticate_user)):
    return hub_lambda_handler_wrapper(
        lambda: timeline.put_reaction_to_comment_item(
            comment_id=comment_id,
            reaction=request_body
        ),
        request=request,
        request_data=request_body.dict()
    )


@timeline_router.delete("/{post_id}")
def delete_post(
        post_id: str,
        request: Request,
        response: Response,
        _: Dict[str, Any] = Depends(authenticate_user)):
    return hub_lambda_handler_wrapper(
        lambda: timeline.delete_logical_timeline_item(post_id=post_id),
        request=request,
    )


@timeline_router.delete("/{post_id}/comment/{comment_id}")
def delete_comment(
        post_id: str,
        comment_id: str,
        request: Request,
        response: Response,
        _: Dict[str, Any] = Depends(authenticate_user)):
    return hub_lambda_handler_wrapper(
        lambda: timeline.delete_logical_comment_item(
            post_id=post_id, comment_id=comment_id),
        request=request,
    )


@timeline_router.get(
    "/list",
    response_model=timeline.FetchListResponseBody[PostItem]
)
# FastAPI automatically recognizes the query parameter when the function argument name matches the query parameter name.
# def get_xx(query_param: Optional[str] = None): is to define a optional query parameter.
# https://fastapi.tiangolo.com/ja/tutorial/query-params/#_3
def get_timeline_list(
        request: Request,
        response: Response,
        timestamp: Optional[int] = Query(None),
        post_id: Optional[str] = Query(None),
        uuid: Optional[str] = Query(None)):
    if uuid:
        return hub_lambda_handler_wrapper_with_rtn_value(
            lambda: timeline.fetch_timeline_list_by_user(
                uuid=uuid,
                timestamp=timestamp,
                post_id=post_id
            ),
            request=request
        )

    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: timeline.fetch_timeline_list(timestamp=timestamp, post_id=post_id),
        request=request
    )


@timeline_router.get(
    "/{post_id}/comment/list",
    response_model=timeline.FetchListResponseBody[CommentItem]
)
def get_comment_list(
        post_id: str,
        request: Request,
        response: Response,
        timestamp: Optional[int] = Query(None),
        comment_id: Optional[str] = Query(None)):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: timeline.fetch_comment_list(
            post_id=post_id,
            timestamp=timestamp,
            comment_id=comment_id
        ),
        request=request
    )


@timeline_router.get(
    "/{post_id}",
    response_model=PostItem
)
def get_timeline(
        post_id: str,
        request: Request,
        response: Response):
    return hub_lambda_handler_wrapper_with_rtn_value(
        lambda: timeline.fetch_timeline_item(post_id=post_id),
        request=request
    )
