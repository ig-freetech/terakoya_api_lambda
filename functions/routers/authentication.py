import os
import sys
from typing import Optional, Annotated
from fastapi import APIRouter, Request, Response, Cookie, status
from functions.models.user import EMPTY_SK
from pydantic import BaseModel
from fastapi.exceptions import HTTPException

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from domain import authentication as auth, user
from utils.process import hub_lambda_handler_wrapper, hub_lambda_handler_wrapper_with_rtn_value

authentication_router = APIRouter()


class AuthAccountRequestBody(BaseModel):
    email: str
    password: str


# Use noun for the endpoint name and express the action with the HTTP method (ex: GET, POST, PUT, DELETE).
# https://www.integrate.io/jp/blog/best-practices-for-naming-rest-api-endpoints-ja/#one
@authentication_router.post("/signup")
def signup(requset_body: AuthAccountRequestBody, request: Request, response: Response):
    return hub_lambda_handler_wrapper_with_rtn_value(lambda: auth.signup(
        email=requset_body.email,
        password=requset_body.password,
    ), request, requset_body.dict())


class DeleteAccountRequestBody(BaseModel):
    uuid: str
    sk: str


# Use post not delete to receive a request body from Client-side. Because delete method does not allow a request body.
@authentication_router.post("/account/delete")
def delete_account(requset_body: DeleteAccountRequestBody, request: Request, response: Response, access_token: Annotated[Optional[str], Cookie()] = None):
    if access_token is None:
        print("アクセストークンがCookieに設定されていません。サインインし直して下さい。")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=""
        )

    def __delete_account():
        auth.delete_user(access_token=access_token, fastApiResponse=response)
        user.delete_item(requset_body.uuid, requset_body.sk)
    return hub_lambda_handler_wrapper(__delete_account, request, requset_body.dict())


@authentication_router.post("/signin")
def sign_in(respose: Response, requset_body: AuthAccountRequestBody, request: Request):
    def __sign_in():
        tokens = auth.signin(requset_body.email, requset_body.password)
        auth.set_cookie_secured(respose, 'access_token', tokens.access_token)
        auth.set_cookie_secured(respose, 'refresh_token', tokens.refresh_token)
        jwt = auth.authenticate_user(request=request, fastApiResponse=respose, access_token=tokens.access_token)
        print(f"jwt: {jwt}")
        uuid = jwt["sub"]
        user_item = user.fetch_item(uuid, EMPTY_SK)
        return user_item
    return hub_lambda_handler_wrapper_with_rtn_value(__sign_in, request, requset_body.dict())


@authentication_router.post("/signout")
def sign_out(response: Response, request: Request):
    return hub_lambda_handler_wrapper(lambda: auth.delete_tokens_from_cookie(response), request)


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
        print("リフレッシュトークンがCookieに設定されていません。サインインし直して下さい。")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is not set in cookie. Please sign in again."
        )
    print(f"refresh_token: ${refresh_token}")
    return hub_lambda_handler_wrapper(lambda: auth.issue_new_access_token(refresh_token, response), request)
