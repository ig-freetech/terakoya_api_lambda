import os
import sys

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(ROOT_DIR_PATH)

from functions.utils.slack import SlackErrorNotification


# def test_slack_error_notification():
#     slack_error_notifier = SlackErrorNotification()
#     response = slack_error_notifier.notify("test", "test", {})
#     assert response.status_code == 200
