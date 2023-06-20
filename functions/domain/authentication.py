import os
import sys
from typing import Any, Dict
import boto3
from jose import jwt, jwk, JWTError
import requests
from fastapi import Response, Depends, HTTPException, status
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


def get_cognito_jwks() -> Dict[str, Any]:
    """
    Returns:
        Dict[str, Any]: { kid: jwk }
    """
    # JWT (JSON Web Token) is a string that encodes a JSON object in Base64 format and separated by a dot in the form of <header>.<payload>.<signature> (ex: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c).
    # JWT itself carrys the information of the user,　while normal token itself does not carry a meaningful information.
    # JSON key/value pair is called a "claim" in JWT. So, key is called "claim name" and value is called "claim value".
    # Claim names reserved in JWT are called "Registered Claim Names" and other claim names are called "Public Claim Names".
    # https://zenn.dev/mikakane/articles/tutorial_for_jwt
    # https://qiita.com/rs_/items/178f549c7a29c30fcbdb

    # The JSON object consists of three parts (header, payload, signature).
    # header: alg(Hash algorithm, ex: "RS256") and typ(Token type, ex: "JWT")
    # payload:
    # - sub(The identifier of the user to be authenticated, usually provided in the form of a URI, ex: "1234567890")
    # - iss(The identifier of Issuer of JWT, ex: "io.exact.sample.jwt")
    # - aud(The identifier of the recipient of JWT)
    # - exp(Expiration time of JWT, ex: 1670085336)
    # - iat(Issued at, ex: 1670081736)
    # signature: A string that is the result of Base64 encoding the header and payload concatenated with a period and encrypted with the secret key of the hash algorithm specified by "alg" in the header.
    # https://developer.mamezou-tech.com/blogs/2022/12/08/jwt-auth/#jwt%E3%81%A8%E3%81%AF

    # Normal token-based authentication requires a request to the server to verify the validity of the token.
    # But JWT can be verified by using the public key　that is provided by Issuer of JWT in the form of a JSON Web Key Set (JWKS).
    # JWK is provided in the form of a JSON object that contains the public keys.
    # JWK is usually published in URL that is provided by Issuer of JWT. For example, AWS publishes JWK in https://cognito-idp.{region}.amazonaws.com/{userPoolId}/.well-known/jwks.json.
    # Signature of JWT is used to verify the validity of JWT by using the public key of JWK with the algorithm specified by "alg" in the header.
    # https://zenn.dev/mikakane/articles/tutorial_for_jwt#%E7%BD%B2%E5%90%8D

    # Get public keys from Cognito User Pool.
    # https://docs.aws.amazon.com/ja_jp/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html#amazon-cognito-user-pools-using-tokens-manually-inspect
    url = f"https://cognito-idp.{AWS_DEFAULT_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}/.well-known/jwks.json"
    response = requests.get(url)
    # jwk.json(sample): { "keys": [ { "kid": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", "alg": "RS256", "kty": "RSA", "e": "AQAB", "n": "1234567890", "use": "sig" } ] }
    jwk_list = response.json()['keys']
    # kid is uid of the public key (and JWK).
    return {jwk['kid']: jwk for jwk in jwk_list}


# tokenUrl is used for only OpenAPI document generation and  Swagger UI to get access token by using email and password.
# https://self-methods.com/fastapi-authentication/
# But FastAPI actually does not use tokenUrl to get access token. So, it doesn't affect the operation of the FastAPI application itself.
# OAuth2PasswordBearer works to get access token from the request header in actual FastAPI application.
# https://fastapi.tiangolo.com/ja/tutorial/security/first-steps/#fastapioauth2passwordbearer
# token is Authorization: Bearer {token(=access_token)} in HTTP request header.
# https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Authorization
# https://qiita.com/h_tyokinuhata/items/ab8e0337085997be04b1
def authenticate_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/signin"))):
    """Verify the signature of the JWT by using the public key of the Cognito User Pool."""
    jwks = get_cognito_jwks()
    try:
        # Decode JWT with python-jose.
        # https://sal-blog.com/cognito%E3%81%AEjwt%E3%81%8B%E3%82%89%E3%83%A6%E3%83%BC%E3%82%B6%E6%83%85%E5%A0%B1%E3%82%92%E5%8F%96%E3%82%8A%E5%87%BA%E3%81%99python-jose/
        # https://docs.aws.amazon.com/ja_jp/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html#amazon-cognito-user-pools-using-tokens-manually-inspect
        header = jwt.get_unverified_header(token)
        alg = header["alg"]
        target_jwk = jwks[header["kid"]]
        if target_jwk is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='JWK not found')
        # Convert JWK to public key object of python-jose.
        pub_key = jwk.construct(target_jwk)
        # Simultaneously verify the signature and decode the payload with the public key and algorithm.
        # PEM is a format for storing and transmitting cryptographic keys.
        # https://zenn.dev/osai/articles/3941f2d1de94f0
        return jwt.decode(token, pub_key.to_pem(), algorithms=[alg])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            # detail is the error message that is displayed in the response body on the client side.
            # https://fastapi.tiangolo.com/ja/tutorial/handling-errors/
            detail='Invalid token',
            # WWW-Authenticate header is used to indicate the authentication method(s) and parameters applicable to the target resource.
            # https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/WWW-Authenticate
            headers={"WWW-Authenticate": "Bearer"})  # Specify the authentication method as "Bearer".


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


# Signout API endpoint is unnecessary because each client (ex: Web browsers, App) can delete the access token and refresh token in Cookie by itself when a user signs out.
# https://qiita.com/wasnot/items/949c6c4efe43ca0fa1cc
# def signout(access_token: str, fastApiResponse: Response):
#     try:
#         # Signs out users from all devices
#         # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp/client/global_sign_out.html
#         cognito.global_sign_out(
#             AccessToken=access_token
#         )
#         fastApiResponse.delete_cookie('access_token')
#         fastApiResponse.delete_cookie('refresh_token')
#     except cognito.exceptions.NotAuthorizedException:
#         raise Exception("Invalid access token")
