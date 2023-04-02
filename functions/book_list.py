
import json
from domain.dynamodb import BookingDynamoDB


def lambda_handler(event, context):
    try:
        target_date = json.loads(event['body'])['target_date']
        item_list = BookingDynamoDB.get_item_list(target_date)
        return {
            'item_list': item_list
        }
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")


if __name__ == '__main__':
    item_list = BookingDynamoDB.get_item_list("2023-01-31")
    print(item_list)
