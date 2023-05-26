print('importing confest.py')
import os
import sys
import requests
import json

from utils.const import headers

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

print(f"ROOT_DIR_PATH: {ROOT_DIR_PATH}")

from functions.utils.dt import DT

SLACK_ERROR_CH_WEBHOOK_URL = os.getenv("SLACK_ERROR_CH_WEBHOOK_URL")

# conftest.py is a file that defines fixtures and plugins for pytest.
# https://docs.pytest.org/en/latest/how-to/writing_plugins.html#conftest-py-plugins
# Test fixtures means functions that are run automatically by pytest before, after or around tests.
# https://www.weblio.jp/content/%E3%83%86%E3%82%B9%E3%83%88%E3%83%95%E3%82%A3%E3%82%AF%E3%82%B9%E3%83%81%E3%83%A3


# pytest_sessionfinish is called just once after all tests have finished.
# https://webbibouroku.com/Blog/Article/pytest#outline__6_4
def pytest_sessionfinish(session, exitstatus):
    """
    Called after whole test run finished, right before returning the exit status to the system.
    """

    if SLACK_ERROR_CH_WEBHOOK_URL is None:
        raise Exception("SLACK_ERROR_CH_WEBHOOK_URL is None")

    passed = len(session.config.pluginmanager.get_plugin('terminalreporter').stats.get('passed', []))
    failed = len(session.config.pluginmanager.get_plugin('terminalreporter').stats.get('failed', []))
    skipped = len(session.config.pluginmanager.get_plugin('terminalreporter').stats.get('skipped', []))

    # Obtain failure reports
    failed_reports = session.config.pluginmanager.get_plugin('terminalreporter').stats.get('failed')

    if failed_reports == None or len(failed_reports) == 0:
        return

    fail_messages = []
    if failed_reports:
        # for idx, elem in enumerate(list):
        # https://uxmilk.jp/8680
        for idx, report in enumerate(failed_reports):
            case_number = idx + 1
            fail_messages.append(
                f"Failed Test Case {case_number}:\n{report.nodeid}\n\nError Message:\n{str(report.longrepr)}\n")

    # TODO: Use replace attachments with blocks
    # https://api.slack.com/block-kit/building#getting_started
    # https://app.slack.com/block-kit-builder

    # HACK: attachments is deprecated
    # https://api.slack.com/reference/messaging/attachments#fields
    # attachments example
    # https://api.slack.com/reference/messaging/attachments#example
    data = {
        "attachments": [
            {
                "pretext": "Test Failed",
                "color": '#ff0000' if failed else '#36a64f',
                "author_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                "fields": [
                    {
                        "title": "Passed Tests",
                        "value": passed,
                        "short": True
                    },
                    {
                        "title": "Failed Tests",
                        "value": failed,
                        "short": True
                    },
                    {
                        "title": "Skipped Tests",
                        "value": skipped,
                        "short": True
                    }
                ],
                "text": "\n".join(fail_messages),
                "ts": DT.CURRENT_JST_DATETIME.timestamp()
            }
        ]
    }

    response = requests.post(SLACK_ERROR_CH_WEBHOOK_URL, headers=headers, data=json.dumps(data))
    assert response.status_code == 200
