from fastapi import APIRouter

booking_router = APIRouter()

# Should use kabab-case to combine words in URL structure
# It's deprecated to combine words with underscore (ex: snake_case) or without any separator (ex: appleorange)
# https://developers.google.com/search/docs/crawling-indexing/url-structure?hl=ja


# async def is useful when you use await in the function
# https://christina04.hatenablog.com/entry/fastapi-def-vs-async-def
@booking_router.get("/excluded-dates")
def get_excluded_dates():
    return {"message": "Hello World"}
