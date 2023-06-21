from typing import Callable
from dataclasses import dataclass, asdict
from typing import Optional
from fastapi import Request

from .slack import SlackErrorNotification

slack_error_notifier = SlackErrorNotification()


# Using dataclass, __init__ method is automatically generated.
# https://yumarublog.com/python/dataclass/
# https://zenn.dev/karaage0703/articles/3508b20ece17d4
@dataclass
class BasicResponseData:
    message: str
    status_code: int


def hub_lambda_handler_wrapper(func: Callable, request: Request, request_data: Optional[dict] = None) -> dict:
    # FastAPI + Lambda has only one log group in CloudWatch Logs for all routes, so it's difficult to distinguish which route is called
    # Define a common log process to distinguish which route is called
    # https://hawksnowlog.blogspot.com/2022/10/fastapi-logging-request-and-response-with-custom.html
    path = f"{request.method}: {request.url.path}"
    print(f"================= {path} =================")
    try:
        func()
        response_data = BasicResponseData("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_data)
        response_data = BasicResponseData(str(e), 500)
    return asdict(response_data)


def hub_lambda_handler_wrapper_with_rtn_value(func: Callable[[], dict], request: Request, request_data: Optional[dict] = None) -> dict:
    path = f"{request.method}: {request.url.path}"
    print(f"================= {path} =================")
    rtn_dict = {}
    try:
        rtn_dict = func()
        response_data = BasicResponseData("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_data)
        response_data = BasicResponseData(str(e), 500)
    return {**asdict(response_data), **rtn_dict}


def lambda_handler_wrapper(event, func: Callable, func_name: Optional[str] = None) -> dict:
    """
    Parameters
    ----------
    func_name : Optional[str]
        The name of the function to be executed. This is used for the error notification.\n
        Required if event.get('routeKey') is None when calling this function from the triggers without API Gateway such as EventBridge or test from the AWS console in Lambda.
    """
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
        path = func_name if func_name != None else event.get('routeKey')
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_body)
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        # raise e
        response_data = BasicResponseData(str(e), 500)
    # asdict() is a function to convert a dataclass object to a dictionary.
    # https://1kara-hajimeru.com/2021/02/1691/
    return asdict(response_data)


def lambda_handler_wrapper_with_rtn_value(event, func: Callable[[], dict], func_name: Optional[str] = None) -> dict:
    """
    Parameters
    ----------
    func_name : Optional[str]
        The name of the function to be executed. This is used for the error notification.\n
        Required if event.get('routeKey') is None when calling this function from the triggers without API Gateway such as EventBridge or test from the AWS console in Lambda.
    """
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
        path = func_name if func_name != None else event.get('routeKey')
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_body)
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        # raise e
        response_data = BasicResponseData(str(e), 500)
    # asdict() is a function to convert a dataclass object to a dictionary.
    # https://1kara-hajimeru.com/2021/02/1691/
    return {**asdict(response_data), **rtn_dict}
