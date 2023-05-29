import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.conf.env import AWS_DEFAULT_REGION, GATEWAY_ID_DEV

base_url = f"https://{GATEWAY_ID_DEV}.execute-api.{AWS_DEFAULT_REGION}.amazonaws.com"

headers = {'Content-Type': 'application/json'}
