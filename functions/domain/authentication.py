import os
import sys
import boto3
from fastapi import Response, Depends
from fastapi.security import OAuth2PasswordBearer

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID

cognito = boto3.client('cognito-idp', aws_access_key_id=AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                       region_name=AWS_DEFAULT_REGION)

if COGNITO_USER_POOL_CLIENT_ID == None or COGNITO_USER_POOL_ID == None:
    raise Exception("COGNITO_USER_POOL_CLIENT_ID or COGNITO_USER_POOL_ID is None")

def set_cookie(fastApiResponse: Response, key: str, value: str):
    """Set access_token and refresh_token to cookie on Server-side"""
    # Include tokens in the response header as a cookie.
    # https://fastapi.tiangolo.com/advanced/response-cookies/
    # Set-Cookie is a HTTP response header to send a cookie from the server to the user agent.
    # https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Set-Cookie
    # Cookie enables to store the user's stateful information (ex: Login information) on the user's browser on HTTP protocol which is stateless.
    # https://qiita.com/mogulla3/items/189c99c87a0fc827520e
    fastApiResponse.set_cookie(
        key=key,
        value=value,
        # Cookie is not accessible from JavaScript by enabling httponly.
        # https://qiita.com/kohekohe1221/items/80ff7a0bba6ac9128f56
        # https://developer.mozilla.org/ja/docs/Web/HTTP/Cookies#%E3%82%BB%E3%82%AD%E3%83%A5%E3%83%AA%E3%83%86%E3%82%A3
        httponly=True,
        # Cookie is send only via HTTPS by enabling secure, and not send via HTTP.
        # https://developer.mozilla.org/ja/docs/Web/HTTP/Cookies#cookie_%E3%81%B8%E3%81%AE%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E5%88%B6%E9%99%90
        secure=True,
        # strict is to return the cookie only if the request originates from the same site not from a third party site (CSRF) and then prevent CSRF attacks.
        # https://laboradian.com/same-site-cookies/#2_SameSite_Same-site_Cookies
        # https://developer.mozilla.org/ja/docs/Web/HTTP/Cookies#samesite_%E5%B1%9E%E6%80%A7
        samesite="strict"
    )

def issue_new_access_token(refresh_token: str, fastApiResponse: Response):
    try:
        # Get new access token by using refresh token.
        response = cognito.initiate_auth(
                ClientId=COGNITO_USER_POOL_CLIENT_ID,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
        )
        auth_result = response['AuthenticationResult']
        set_cookie(fastApiResponse, 'access_token', auth_result['AccessToken'])
        set_cookie(fastApiResponse, 'refresh_token', auth_result['RefreshToken'])
    except cognito.exceptions.NotAuthorizedException:
        raise Exception("Invalid refresh token")
    

# tokenUrl is used for only OpenAPI document generation and  Swagger UI to get access token by using email and password.
# https://self-methods.com/fastapi-authentication/
# But FastAPI actually does not use tokenUrl to get access token. So, it doesn't affect the operation of the FastAPI application itself.
# OAuth2PasswordBearer works to get access token from the request header in actual FastAPI application.
# https://fastapi.tiangolo.com/ja/tutorial/security/first-steps/#fastapioauth2passwordbearer
def authenticate_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/signin"))):
    pass

def signup(email: str, password: str):
    try:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/sign_up.html    
        cognito.sign_up(
                ClientId=COGNITO_USER_POOL_CLIENT_ID,
                Username=email,
                Password=password,
                # Specify user attributes as name-value pairs to be stored as the user profile in User Pool.
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': email
                    },
                ],
                # Attributes in ClientMetadata are passed to the Lambda trigger (ex: PostConfirmation trigger etc.)
                # email is used in PostConfirmation trigger to add a record to User table in DynamoDB.
                ClientMetadata={
                    'email': email,
                }
            )
    except cognito.exceptions.UsernameExistsException:
        raise Exception("Specified email is already exists")
    
def signin(email: str, password: str, fastApiResponse: Response):
    try:
        # Get tokens by using email and password.
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/initiate_auth.html
        response = cognito.initiate_auth(
                ClientId=COGNITO_USER_POOL_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
        # AuthenticationResult is a dictionary that contains the access token , ID token, and refresh token.
        auth_result = response['AuthenticationResult']

        set_cookie(fastApiResponse, 'access_token', auth_result['AccessToken'])
        set_cookie(fastApiResponse, 'refresh_token', auth_result['RefreshToken'])
    except cognito.exceptions.NotAuthorizedException:
        raise Exception("Invalid email or password")

def signout(access_token: str, fastApiResponse: Response):
    try:
        # Signs out users from all devices
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/global_sign_out.html
        cognito.global_sign_out(
                AccessToken=access_token
            )
        fastApiResponse.delete_cookie('access_token')
        fastApiResponse.delete_cookie('refresh_token')
    except cognito.exceptions.NotAuthorizedException:
        raise Exception("Invalid access token")

