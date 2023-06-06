import os
import sys
import json
import requests
from typing import Optional

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from conf.env import SLACK_ERROR_CH_WEBHOOK_URL, STAGE
from conf.util import IS_PROD


class SlackErrorNotification:
    # Optional[type] means type or None
    # https://python.ms/union-and-optional/#_2-optional-%E5%9E%8B
    def __init__(self) -> None:
        if SLACK_ERROR_CH_WEBHOOK_URL is None:
            raise ValueError("SLACK_ERROR_CH_WEBHOOK_URL is None")
        self.webhook_url = SLACK_ERROR_CH_WEBHOOK_URL

    def notify(self, path: str, msg: str, request_data: Optional[dict]) -> requests.Response:
        # Create payload with layout blocks instead of attachments because attachments is deprecated.
        # https://api.slack.com/block-kit/building#getting_started
        # https://api.slack.com/reference/block-kit/blocks#section
        # https://api.slack.com/reference/messaging/attachments
        payload = {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"⛔️Error happend! [{STAGE}]",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*In:*\n{path}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Error Message:*\n{msg}"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Request Data*:\n{json.dumps(request_data, indent=4) if request_data != None else 'None'}"
                    }
                },
            ]
        }
        if IS_PROD:
            payload["blocks"].insert(0, {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    # <!channel> is a Slack command to notify all members in the channel.
                    # https://qiita.com/ryo-yamaoka/items/7677ee4486cf395ce9bc
                    "text": "<!channel>"
                }
            })
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.webhook_url, headers=headers, data=json.dumps(payload))
        return response
