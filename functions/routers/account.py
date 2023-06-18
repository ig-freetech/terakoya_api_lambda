import os
import sys
from fastapi import APIRouter, Request
from pydantic import BaseModel

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from domain.auth import signup
from utils.process import hub_lambda_handler_wrapper

account_router = APIRouter()


class AccountRequestBody(BaseModel):
    email: str
    password: str


@account_router.post("/")
def create_account(requset_body: AccountRequestBody, request: Request):
    return hub_lambda_handler_wrapper(lambda: signup(requset_body.email, requset_body.password), request, requset_body.dict())


@account_router.delete("/")
def delete_account(request: Request):
    return "delete_account"
