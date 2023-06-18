import os
import sys
import boto3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID

cognito = boto3.client('cognito-idp', aws_access_key_id=AWS_ACCESS_KEY_ID,
                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                       region_name=AWS_DEFAULT_REGION)


def signup(email: str, password: str):
    if COGNITO_USER_POOL_CLIENT_ID == None or COGNITO_USER_POOL_ID == None:
        raise Exception("COGNITO_USER_POOL_CLIENT_ID or COGNITO_USER_POOL_ID is None")
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
