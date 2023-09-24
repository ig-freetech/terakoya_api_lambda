from typing import Callable
from typing import Optional
from fastapi import Request, status

from fastapi.exceptions import HTTPException

from .slack import SlackErrorNotification

slack_error_notifier = SlackErrorNotification()


def hub_lambda_handler_wrapper(func: Callable, request: Request, request_data: Optional[dict] = None) -> Optional[dict]:
    # FastAPI + Lambda has only one log group in CloudWatch Logs for all routes, so it's difficult to distinguish which route is called
    # Define a common log process to distinguish which route is called
    # https://hawksnowlog.blogspot.com/2022/10/fastapi-logging-request-and-response-with-custom.html
    path = f"{request.method}: {request.url.path}"
    print(f"================= {path} =================")
    try:
        func()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_data)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def hub_lambda_handler_wrapper_with_rtn_value(func: Callable[[], dict], request: Request, request_data: Optional[dict] = None) -> dict:
    path = f"{request.method}: {request.url.path}"
    print(f"================= {path} =================")
    try:
        return func()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_data)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def lambda_handler_wrapper(event, func: Callable, func_name: Optional[str] = None) -> Optional[dict]:
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
    try:
        func()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        path = func_name if func_name != None else event.get('routeKey')
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_body)
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
    try:
        return func()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        path = func_name if func_name != None else event.get('routeKey')
        slack_error_notifier.notify(path=path, msg=str(e), request_data=request_body)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
