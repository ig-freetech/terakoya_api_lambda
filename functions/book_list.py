
from domain.dynamodb import BookingDynamoDB


def lambda_handler(event, context):
    try:
        item_list = BookingDynamoDB.get_item_list_after_today()
        return {
            'itemList': item_list
        }
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")


if __name__ == '__main__':
    item_list = BookingDynamoDB.get_item_list_after_today()
    print(item_list)
