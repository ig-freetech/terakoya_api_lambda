# This Lambda function is triggered by PostConfirmation trigger of Cognito User Pool. i.e., when a user clicks the confirmation link in the confirmation email.
def lambda_handler(event, context):
    print(f"event: {event}")
    user_name = event['userName']
    user_pool_id = event['userPoolId']

    # TODO: Create a user info record in DynamoDB

    # PostConfirmation trigger must return event
    # https://docs.aws.amazon.com/ja_jp/cognito/latest/developerguide/user-pool-lambda-post-confirmation.html
    return event
