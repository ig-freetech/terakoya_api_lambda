import os
import sys
import boto3

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, STAGE


def cp_data_between_tables(table_name_from: str, table_name_to: str):
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID,
                              aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)
    table_from = dynamodb.Table(table_name_from)
    table_to = dynamodb.Table(table_name_to)

    response = table_from.scan()
    items = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table_from.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    with table_to.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


if __name__ == '__main__':
    # cp_data_between_tables('booking_dev', 'terakoya-booking-renewal-dev')
    cp_data_between_tables('booking_prod', 'terakoya-booking-renewal-prod')
