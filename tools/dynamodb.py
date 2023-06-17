import os
import sys
import json
import boto3
from decimal import Decimal

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

tmp_dpath = os.path.join(os.path.dirname(__file__), 'tmp')

dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=AWS_DEFAULT_REGION)


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


def write_items_to_table(table_name_to: str, items: list) -> None:
    table_to = dynamodb.Table(table_name_to)
    with table_to.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def load_items_from_table(stored_json_fpath: str) -> list:
    if (not os.path.exists(stored_json_fpath)):
        raise Exception(f'File does not exist: {stored_json_fpath}')
    with open(stored_json_fpath, 'r') as f:
        # DynamoDB cannot accept float type, so we need to convert it to Decimal.
        items = json.load(f, parse_float=Decimal)
        return items


def save_items_to_json(table_name_from: str) -> list:
    stored_json_fpath = os.path.join(tmp_dpath, f'{table_name_from}.json')
    table_from = dynamodb.Table(table_name_from)

    response = table_from.scan()
    items = response['Items']
    while 'LastEvaluatedKey' in response:
        response = table_from.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])

    with open(stored_json_fpath, 'w') as f:
        # item has Decimal type field, so we need to convert it to float using DecimalEncoder so that it can be serialized to JSON.
        json.dump(items, f, cls=DecimalEncoder)

    return items


def cp_items_between_tables(table_name_from: str, table_name_to: str) -> None:
    items = save_items_to_json(table_name_from)
    write_items_to_table(table_name_to, items)


def cp_items_from_json_to_table(stored_json_fpath: str, table_name_to: str):
    items = load_items_from_table(stored_json_fpath)
    write_items_to_table(table_name_to, items)


if __name__ == '__main__':
    # cp_items_between_tables('terakoya-booking-renewal-dev', 'prod-copied')
    # cp_items_from_json_to_table(os.path.join(tmp_dpath, 'copied_items.json'), 'terakoya-dev-booking')
    save_items_to_json('terakoya-dev-booking')
