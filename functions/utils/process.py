from typing import Callable
from dataclasses import dataclass, asdict

# Using dataclass, __init__ method is automatically generated.
# https://yumarublog.com/python/dataclass/
# https://zenn.dev/karaage0703/articles/3508b20ece17d4


@dataclass
class ResponseBody:
    message: str
    status_code: int


def lambda_handler_wrapper(event, func: Callable) -> dict:
    print(f"Request Body: {event['body']}")
    response_body: ResponseBody
    try:
        func()
        response_body = ResponseBody("Success", 200)
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        # raise e
        response_body = ResponseBody(str(e), 500)
    # asdict() is a function to convert a dataclass object to a dictionary.
    # https://1kara-hajimeru.com/2021/02/1691/
    return asdict(response_body)
