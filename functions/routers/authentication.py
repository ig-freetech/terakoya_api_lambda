import os
import sys
from typing import Optional, Annotated
from fastapi import APIRouter, Request, Response, Cookie, status
from pydantic import BaseModel
from fastapi.exceptions import HTTPException

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from functions.domain.authentication import issue_new_access_token, signup, signin
from utils.process import hub_lambda_handler_wrapper

authentication_router = APIRouter()


class AuthAccountRequestBody(BaseModel):
    email: str
    password: str


# Use noun for the endpoint name and express the action with the HTTP method (ex: GET, POST, PUT, DELETE).
# https://www.integrate.io/jp/blog/best-practices-for-naming-rest-api-endpoints-ja/#one
@authentication_router.post("/account")
def create_account(requset_body: AuthAccountRequestBody, request: Request):
    return hub_lambda_handler_wrapper(lambda: signup(requset_body.email, requset_body.password), request, requset_body.dict())


class DeleteAccountRequestBody(BaseModel):
    email: str


@authentication_router.delete("/account")
def delete_account(requset_body: DeleteAccountRequestBody, request: Request):
    return "delete_account"


@authentication_router.post("/signin")
def sign_in(respose: Response, requset_body: AuthAccountRequestBody, request: Request):
    return hub_lambda_handler_wrapper(lambda: signin(requset_body.email, requset_body.password, respose), request, requset_body.dict())


# It's recommended to use Annotated[Optional[str], Cookie()] = None instead of Optional[str] = Cookie(None) to get a cookie value.
# https://fastapi.tiangolo.com/tutorial/cookie-params/#__tabbed_2_2
# Cookie(None) returns None when the cookie is not set, but Annotated[Optional[str], Cookie()] = None returns None when the cookie is set but the value is None.
# <value_cookie> can be obtained by <key_cookie>: Annotated[Optional[str], Cookie()] = None. (ex: access_token: Annotated[Optional[str], Cookie()] = None)
# Annotated is a type annotation that can be used to add metadata to a type.
# https://yiskw713.hatenablog.com/entry/2022/01/25/233000


@authentication_router.post("/refresh-token")
def refresh_token(response: Response, request: Request, refresh_token: Annotated[Optional[str], Cookie()] = None):
    if refresh_token is None:
        # 403 Forbidden
        # Access is permanently prohibited due to insufficient authorization to access the resource, etc. So, re-authentication will not change the result.
        # https://developer.mozilla.org/ja/docs/Web/HTTP/Status/403
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token is not set.")
    return hub_lambda_handler_wrapper(lambda: issue_new_access_token(refresh_token, response), request)
