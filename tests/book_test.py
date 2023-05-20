import os
import sys
import json
import boto3

from samples.booking import book_request_body

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE

from functions.utils.dt import DT


def test_lambda_handler_success():
    client = boto3.client('lambda', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)
    response = client.invoke(
        FunctionName=f'terakoya-booking-renewal-dev-book',
        InvocationType='RequestResponse',
        Payload=json.dumps({
            "body": book_request_body
        })
    )
    print(response)
    print(response['Payload'])
    assert response['StatusCode'] == 200
    # TODO: DB に当該データが登録されていることを確認する
