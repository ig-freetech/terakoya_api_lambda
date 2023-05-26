import os
from slack_sdk.webhook import WebhookClient

# Getting Started
# https://shikaku-mafia.com/from-python-to-slack/

# Set up Incoming Webhooks in the following page
# https://my.slack.com/services/new/incoming-webhook/

SLACK_ERROR_CH_WEBHOOK_URL = os.getenv("SLACK_ERROR_CH_WEBHOOK_URL")


class SlackClient:
    @classmethod
    def send_error_message_to_slack(cls, message: str) -> None:
        if SLACK_ERROR_CH_WEBHOOK_URL is None:
            raise Exception("SLACK_ERROR_CH_WEBHOOK_URL is None")
        webhook = WebhookClient(SLACK_ERROR_CH_WEBHOOK_URL)
        response = webhook.send(text=message)
        assert response.status_code == 200
        assert response.body == "ok"
