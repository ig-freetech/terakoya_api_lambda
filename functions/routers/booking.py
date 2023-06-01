import os
import sys
from fastapi import APIRouter

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from conf.env import S3_TERAKOYA_BUCKET_NAME, STAGE
from utils.aws import s3_client
from utils.process import hub_lambda_handler_wrapper_with_rtn_value, hub_lambda_handler_wrapper

EXCLUDED_DATES_CSV_FKEY = f"api/booking/excluded_dates_{STAGE}.csv"

booking_router = APIRouter()


def fetch_excluded_dates(excluded_dates_csv_fkey: str = EXCLUDED_DATES_CSV_FKEY) -> dict:
    if S3_TERAKOYA_BUCKET_NAME is None:
        raise Exception("S3_TERAKOYA_BUCKET_NAME is not defined")
    # csv object is returned in Body field (StreamingBody Type) of the response
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_object
    csv_obj = s3_client.get_object(Bucket=S3_TERAKOYA_BUCKET_NAME, Key=excluded_dates_csv_fkey)
    # convert bytes to string using decode()
    # https://analytics-note.xyz/aws/boto3-s3-put-get/
    csv_text = csv_obj["Body"].read().decode("utf-8")  # ex: '2023-06-03\n2023-06-10\n2023-06-17\n2023-06-24'
    # splitlines() returns a list of lines delimited by \n
    # https://step-learn.com/article/python/035-splitlines.html
    excluded_dates = csv_text.splitlines()
    return {"dates": excluded_dates}

# Should use kabab-case to combine words in URL structure
# It's deprecated to combine words with underscore (ex: snake_case) or without any separator (ex: appleorange)
# https://developers.google.com/search/docs/crawling-indexing/url-structure?hl=ja


# async def is useful when you use await in the function
# https://christina04.hatenablog.com/entry/fastapi-def-vs-async-def
@booking_router.get("/excluded-dates")
def get_excluded_dates():
    return hub_lambda_handler_wrapper_with_rtn_value(fetch_excluded_dates)


def update_excluded_dates(dates: list[str], excluded_dates_csv_fkey: str = EXCLUDED_DATES_CSV_FKEY):
    # The description of the format of the parameter is as follows
    # https://qiita.com/simonritchie/items/49e0813508cad4876b5a#%E5%BC%95%E6%95%B0%E3%81%AE%E6%9B%B8%E3%81%8D%E6%96%B9
    """
    Parameters
    ----------
    dates : format of ["YYYY-MM-DD", "YYYY-MM-DD", ...]
    """
    if S3_TERAKOYA_BUCKET_NAME is None:
        raise Exception("S3_TERAKOYA_BUCKET_NAME is not defined")
    # Update in the shape of "YYYY-MM-DD,YYYY-MM-DD,YYYY-MM-DD, ..."
    csv_text = "\n".join(dates)
    s3_client.put_object(Bucket=S3_TERAKOYA_BUCKET_NAME, Key=excluded_dates_csv_fkey, Body=csv_text.encode("utf-8"))


@booking_router.put("/excluded-dates")
def put_excluded_dates(dates: list[str]):
    return hub_lambda_handler_wrapper(lambda: update_excluded_dates(dates))
