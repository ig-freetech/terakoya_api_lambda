import json


class Account():
    def __init__(self, event) -> None:
        request_body = json.loads(event["body"])
        self.email = request_body["email"]
        self.password = request_body["password"]
        self.is_valid_user = self.email == 'terakoyaf69e5@admin.stopgap' and self.password == 'admin2021terakoya'


def lambda_handler(event, context):
    print(f"Request body: {event['body']}")
    try:
        user = Account(event)
        if (user.is_valid_user):
            return {
                'result_type': 1,
                'message': 'Success'
            }
        else:
            raise Exception("Failed login")
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        return {
            'result_type': 0,
            'message': 'Failed'
        }
