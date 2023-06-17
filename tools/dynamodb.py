import os
import sys
import json
import boto3
from decimal import Decimal

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

stored_json_fpath = os.path.join(os.path.dirname(__file__), 'tmp', 'copied_items.json')


class DecimalEncoder(json.JSONEncoder):
    """
    Decimal type cannot be serialized to JSON, so we need to convert it to float.
    https://qiita.com/ekzemplaro/items/5fa8900212252ab554a3
    https://pg-chain.com/python-int-float-decimal
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


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

    with open(stored_json_fpath, 'w') as f:
        # item has Decimal type field, so we need to convert it to float using DecimalEncoder so that it can be serialized to JSON.
        json.dump(items, f, cls=DecimalEncoder)

    with open(stored_json_fpath, 'r') as f:
        # DynamoDB cannot accept float type, so we need to convert it to Decimal.
        items = json.load(f, parse_float=Decimal)

    with table_to.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


if __name__ == '__main__':
    # cp_data_between_tables('booking_dev', 'terakoya-booking-renewal-dev')
    cp_data_between_tables('terakoya-booking-renewal-dev', 'prod-copied')
