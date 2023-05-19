from typing import Callable


def lambda_handler_wrapper(event, func: Callable):
    print(f"Request Body: {event['body']}")
    try:
        func()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")
        # re-raise the exception to notify the error to the caller (ex: client)
        # https://docs.python.org/ja/3.9/tutorial/errors.html#raising-exceptions
        raise e
