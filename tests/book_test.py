import os
import sys
import json
import boto3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE


def test_lambda_handler():
    client = boto3.client('lambda', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)
    response = client.invoke(
        FunctionName=f'terakoya-booking-renewal-{STAGE}-book',
        InvocationType='RequestResponse',
        # TODO: remarks にテスト実行時の日時を入れてテスト結果を確認しやすくする
        Payload=json.dumps({
            "body": json.dumps({
                "name": "I.G",
                "email": "i.g.freetech2021@gmail.com",
                "terakoya_type": 1,
                "attendance_date_list": [
                    "2023-05-16"
                ],
                "arrival_time": 1,
                "grade": 2,
                "terakoya_experience": 2,
                "study_subject": 8,
                "study_subject_detail": "AHAHA",
                "study_style": 1,
                "school_name": "",
                "first_choice_school": "",
                "course_choice": 999,
                "future_free": "",
                "like_thing_free": "",
                "how_to_know_terakoya": 999,
                "remarks": "AHAHA"
            })
        })
    )
    print(response)
    print(response['Payload'])
    assert response['StatusCode'] == 200
    # TODO: DB に当該データが登録されていることを確認する
