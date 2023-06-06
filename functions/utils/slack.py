import os
import sys
import slackweb
from typing import Optional

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from conf.env import SLACK_ERROR_CH_WEBHOOK_URL


class SlackNotification:
    # Optional[type] means type or None
    # https://python.ms/union-and-optional/#_2-optional-%E5%9E%8B
    def __init__(self, webhook_url: Optional[str]) -> None:
        if webhook_url is None:
            raise ValueError("webhook_url is None")
        self.__slack = slackweb.Slack(url=webhook_url)

    def notify(self, text: str) -> None:
        self.__slack.notify(text=text)


class SlackErrorNotifier:
    def __init__(self) -> None:
        self.__slack = SlackNotification(SLACK_ERROR_CH_WEBHOOK_URL)

    def notify(self, errorMsg: str) -> None:
        self.__slack.notify(text=errorMsg)
