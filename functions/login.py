
import json


class Account():
    def __init__(self, event) -> None:
        request_body = json.loads(event["body"])
        self.email = request_body["email"]
        self.password = request_body["password"]

    def isValidUser(self) -> bool:
        return self.email == 'terakoyaf69e5@test.stopgap' and self.password == 'AIzaSyDlP_gO0lse_wEZxmMBUbPtjLf5xgcL5Qk'


def lambda_handler(event, context):
    try:
        user = Account(event)
        if (user.isValidUser):
            return {
                "statusCode": 200,
                "message": "Success"
            }
        else:
            raise Exception("Failed login")
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
