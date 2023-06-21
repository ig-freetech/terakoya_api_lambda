import os
import sys
import time
import json
import requests
import boto3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import COGNITO_USER_POOL_ID, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE
from functions.domain import authentication as auth, user
from functions.models.user import EMPTY_SK, UserItem, AUTHORITY
from tests.samples.user import email, password, account_request_body_json, post_confirmation_payload_json, updated_name, updated_staff_in_charge, updated_number_of_attendances, updated_attendance_rate, update_user_item_json
from tests.utils.const import base_url, headers

lambda_client = boto3.client('lambda', aws_access_key_id=AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                             region_name=AWS_DEFAULT_REGION)


class Test:
    def test_agw_from_create_to_delete_user(self):
        if COGNITO_USER_POOL_ID is None:
            raise Exception("COGNITO_USER_POOL_ID is None")

        response_create_account = requests.post(
            f"{base_url}/account", headers=headers, data=json.dumps(account_request_body_json))
        print(f"response_create_account: {response_create_account}")
        response_body_create_account = response_create_account.json()
        print(f"response_create_account_body: {response_body_create_account}")
        assert response_create_account.status_code == 200
        assert response_body_create_account.get("status_code") == 200

        uuid = response_body_create_account.get("uuid")
        auth.cognito.admin_confirm_sign_up(UserPoolId=COGNITO_USER_POOL_ID, Username=uuid)
        time.sleep(3)  # wait for PostConfirmation trigger to be finished
        lambda_client.invoke(
            FunctionName=f"terakoya-{STAGE}-auth-post-confirmation",
            InvocationType='RequestResponse',
            Payload=json.dumps({**post_confirmation_payload_json, "userName": uuid})
        )

        response_signin = requests.post(f"{base_url}/signin", headers=headers,
                                        data=json.dumps(account_request_body_json))
        print(f"response_signin: {response_signin}")
        response_body_signin = response_signin.json()
        # print(f"response_body_signin: {response_body_signin}")
        assert response_create_account.status_code == 200
        assert response_body_create_account.get("status_code") == 200
        assert response_body_signin.get("uuid") == uuid

        response_get_user = requests.get(f"{base_url}/user/{uuid}", headers=headers)
        print(f"response_get_user: {response_get_user}")
        response_body_get_user = response_get_user.json()
        # print(f"response_body_get_user: {response_body_get_user}")
        assert response_get_user.status_code == 200
        assert response_body_get_user.get("status_code") == 200
        user_item = UserItem(**response_body_get_user.get("item"))
        assert user_item.email == email
        assert user_item.name == ""
        assert user_item.staff_in_charge == []
        assert user_item.number_of_attendances == 0
        assert user_item.attendance_rate == 0.0
        assert user_item.is_admin.value == AUTHORITY.NOT_ADMIN.value

        response_update_user = requests.put(f"{base_url}/user/{uuid}", headers=headers,
                                            data=json.dumps(update_user_item_json))
        print(f"response_update_user: {response_update_user}")
        response_body_update_user = response_update_user.json()
        # print(f"response_body_update_user: {response_body_update_user}")
        assert response_update_user.status_code == 200
        assert response_body_update_user.get("status_code") == 200

        response_get_updated_user = requests.get(f"{base_url}/user/{uuid}", headers=headers)
        print(f"response_get_updated_user: {response_get_updated_user}")
        response_body_get_updated_user = response_get_updated_user.json()
        # print(f"response_body_get_updated_user: {response_body_get_updated_user}")
        assert response_get_updated_user.status_code == 200
        assert response_body_get_updated_user.get("status_code") == 200
        updated_user_item = UserItem(**response_body_get_updated_user.get("item"))
        assert updated_user_item.email == email
        assert updated_user_item.name == updated_name
        assert updated_user_item.staff_in_charge == updated_staff_in_charge
        assert updated_user_item.number_of_attendances == updated_number_of_attendances
        assert updated_user_item.attendance_rate == updated_attendance_rate
        assert updated_user_item.is_admin.value == AUTHORITY.ADMIN.value

        # Include cookie returned from signin because delete user api requires cookie including access token
        # https://show-time-blog.com/it-knowledge/python/1014/#toc12
        response_delete_user = requests.delete(
            f"{base_url}/account", headers=headers, cookies=response_signin.cookies)
        print(f"response_delete_user: {response_delete_user}")
        response_body_delete_user = response_delete_user.json()
        # print(f"response_body_delete_user: {response_body_delete_user}")
        assert response_delete_user.status_code == 200
        assert response_body_delete_user.get("status_code") == 200

        response_signin_after_deleted = requests.post(f"{base_url}/signin", headers=headers,
                                                      data=json.dumps(account_request_body_json))
        print(f"response_signin: {response_signin_after_deleted}")
        response_body_signin_after_deleted = response_signin_after_deleted.json()
        # print(f"response_body_signin: {response_body_signin}")
        assert response_signin_after_deleted.status_code == 200
        assert response_body_signin_after_deleted.get("status_code") == 500  # Internal Server Error
        assert response_body_signin_after_deleted.get(
            "message") == "An error occurred (UserNotFoundException) when calling the InitiateAuth operation: User does not exist."

    def test_func_from_create_to_delete_user(self):
        if COGNITO_USER_POOL_ID is None:
            raise Exception("COGNITO_USER_POOL_ID is None")

        signup_response = auth.signup(email, password)
        if signup_response is None:
            raise Exception("UUID is None")
        uuid = signup_response['uuid']
        print(f"uuid: {uuid}")

        auth.cognito.admin_confirm_sign_up(UserPoolId=COGNITO_USER_POOL_ID, Username=uuid)
        time.sleep(3)  # wait for PostConfirmation trigger to be finished

        login_response = auth.signin(email, password)
        print(f"login_response: {login_response}")

        user_item = UserItem(**user.fetch_item(uuid, EMPTY_SK))
        print(f"user_item: {user_item.dict()}")
        # Initial values
        assert user_item.email == email
        assert user_item.name == ""
        assert user_item.staff_in_charge == []
        assert user_item.number_of_attendances == 0
        assert user_item.attendance_rate == 0.0
        assert user_item.is_admin.value == AUTHORITY.NOT_ADMIN.value

        user.update_item(UserItem(
            # Merge values with dict unpacking operator (**) in Python (ex: dict1 = { **dict1, "key1": "value1", "key2": "value2", ... })
            # https://zenn.dev/megane_otoko/articles/084_dict_process
            **{
                **user_item.dict(),
                "name": updated_name,
                "staff_in_charge": updated_staff_in_charge,
                "number_of_attendances": updated_number_of_attendances,
                "attendance_rate": updated_attendance_rate,
                "is_admin": AUTHORITY.ADMIN.value
            },
        ))
        updated_user_item = UserItem(**user.fetch_item(uuid, EMPTY_SK))
        print(f"updated_user_item: {updated_user_item.dict()}")
        # Updated values
        assert updated_user_item.email == email
        assert updated_user_item.name == updated_name
        assert updated_user_item.staff_in_charge == updated_staff_in_charge
        assert updated_user_item.number_of_attendances == updated_number_of_attendances
        assert updated_user_item.attendance_rate == updated_attendance_rate
        assert updated_user_item.is_admin.value == AUTHORITY.ADMIN.value

        auth.delete_user(access_token=login_response.access_token)
        user.delete_item(uuid, EMPTY_SK)

        try:
            auth.signin(email, password)
            raise Exception("(Test Failed) Succeeded to sign in. Maybe the user is not deleted.")
        except auth.cognito.exceptions.UserNotFoundException:
            print("(Test Success) Failed to sign in. Because the user is deleted.")
