from typing import Callable
from dataclasses import dataclass, asdict
from slack import SlackErrorNotifier

# Using dataclass, __init__ method is automatically generated.
# https://yumarublog.com/python/dataclass/
# https://zenn.dev/karaage0703/articles/3508b20ece17d4

slack_error_notifier = SlackErrorNotifier()


@dataclass
class BasicResponseData:
    message: str
    status_code: int


def hub_lambda_handler_wrapper(func: Callable) -> dict:
    try:
        func()
        response_data = BasicResponseData("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(str(e))
        response_data = BasicResponseData(str(e), 500)
    return asdict(response_data)


def hub_lambda_handler_wrapper_with_rtn_value(func: Callable[[], dict]) -> dict:
    rtn_dict = {}
    try:
        rtn_dict = func()
        response_data = BasicResponseData("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(str(e))
        response_data = BasicResponseData(str(e), 500)
    return {**asdict(response_data), **rtn_dict}


def lambda_handler_wrapper(event, func: Callable) -> dict:
    # Dict.get('key_name') returns None if the key doesn't exist.
    # https://note.nkmk.me/python-dict-get/
    request_body = event.get('body')
    if request_body != None:
        print(f"Request Body: {request_body}")
    response_data: BasicResponseData
    try:
        func()
        response_data = BasicResponseData("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(str(e))
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        # raise e
        response_data = BasicResponseData(str(e), 500)
    # asdict() is a function to convert a dataclass object to a dictionary.
    # https://1kara-hajimeru.com/2021/02/1691/
    return asdict(response_data)


def lambda_handler_wrapper_with_rtn_value(event, func: Callable[[], dict]) -> dict:
    request_body = event.get('body')
    if request_body != None:
        print(f"Request Body: {request_body}")
    response_data: BasicResponseData
    rtn_dict = {}
    try:
        rtn_dict = func()
        response_data = BasicResponseData("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(str(e))
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        # raise e
        response_data = BasicResponseData(str(e), 500)
    # asdict() is a function to convert a dataclass object to a dictionary.
    # https://1kara-hajimeru.com/2021/02/1691/
    return {**asdict(response_data), **rtn_dict}
