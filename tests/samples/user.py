import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_DEFAULT_REGION, COGNITO_USER_POOL_ID, COGNITO_USER_POOL_CLIENT_ID
from functions.models.user import GRADE, COURSE_CHOICE, HOW_TO_KNOW_TERAKOYA, AUTHORITY
from functions.utils.dt import DT

email = "i.g.freetech2021@gmail.com"
password = "Test1234"

account_request_body_json = {
    "email": email,
    "password": password,
}

post_confirmation_payload_json = {
    "version": "1",
    "region": AWS_DEFAULT_REGION,
    "userPoolId": COGNITO_USER_POOL_ID,
    "userName": "Dummy",  # TODO: to be merged (uuid)
    "callerContext": {
        "awsSdkVersion": "aws-sdk-js-2.148.0",
        "clientId": COGNITO_USER_POOL_CLIENT_ID
    },
    "triggerSource": "PostConfirmation_ConfirmSignUp",
    "request": {
        "userAttributes": {
            "sub": "Dummy",  # Not to be merged (uuid) because it is not used in post confirmation trigger
            "email_verified": "true",
            "cognito:user_status": "CONFIRMED",
            "email": email
        }
    },
    "response": {}
}

updated_name = "Updated Test Name"
updated_staff_in_charge = ["Updated Test Staff 1", "Updated Test Staff 2"]
updated_number_of_attendances = 1
updated_attendance_rate = 0.5

update_user_item_json = {
    "uuid": "Dummy",  # TODO: to be merged (uuid)
    "sk": "EMPTY_SK",
    "email": email,
    "name": updated_name,
    "nickname": "Test Nickname",
    "school": "Test School",
    "grade": GRADE.OTHER.value,
    "course_choice": COURSE_CHOICE.NULL.value,
    "staff_in_charge": updated_staff_in_charge,
    "future_path": "This is test.\n\nThis is pytest.",
    "like_thing": "This is test.\n\nThis is pytest.",
    "how_to_know_terakoya": HOW_TO_KNOW_TERAKOYA.NULL.value,
    "number_of_attendances": updated_number_of_attendances,
    "attendance_rate": updated_attendance_rate,
    "is_admin": AUTHORITY.ADMIN.value,
    "created_at_iso": DT.CURRENT_JST_ISO_8601_DATETIME,
    "updated_at_iso": "",
}
