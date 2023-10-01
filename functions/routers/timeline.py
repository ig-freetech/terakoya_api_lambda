import os
import sys
from fastapi import APIRouter, Request, Response

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from models.timeline import PostItem, CommentItem
from utils.process import hub_lambda_handler_wrapper_with_rtn_value

timeline_router = APIRouter()


@timeline_router.get("/", response_model=PostItem)
def get_timeline(request: Request, response: Response):
    def __get_timeline():
        timeline = []
        return timeline
    return hub_lambda_handler_wrapper_with_rtn_value(__get_timeline, request)
