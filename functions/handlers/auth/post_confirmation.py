import os
import sys

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(FUNCTIONS_DIR_PATH)

from domain.user import insert_item
from models.user import UserItem
from utils.slack import SlackErrorNotification

slack_error_notifier = SlackErrorNotification()

# This Lambda function is triggered by PostConfirmation trigger of Cognito User Pool. i.e., when a user clicks the confirmation link in the confirmation email.
def lambda_handler(event, context):
    print(f"event: {event}")
    try: 
        user_name = event['userName']
        user_email = event['request']['userAttributes']['email']
        user_item = UserItem(uuid=user_name, email=user_email)
        print(f"user_item: {user_item.dict()}")

        insert_item(user_item)

        # PostConfirmation trigger must return event
        # https://docs.aws.amazon.com/ja_jp/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html
        return event
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(path="post_confirmation", msg=str(e), request_data=event)
