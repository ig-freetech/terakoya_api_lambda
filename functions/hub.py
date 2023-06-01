from fastapi import FastAPI, APIRouter, Request
from fastapi.routing import APIRoute
from mangum import Mangum
import logging
from typing import Callable

from .routers import booking_router

app = FastAPI()

# FastAPI + Lambda has only one log group in CloudWatch Logs for all routes, so it's difficult to distinguish which route is called
# Define a common log process to distinguish which route is called using Custom APIRoute like below
# https://hawksnowlog.blogspot.com/2022/10/fastapi-logging-request-and-response-with-custom.html

logger = logging.getLogger(__name__)


class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            logger.info(f"================= {request.url.path} =================")
            response = await original_route_handler(request)
            return response

        return custom_route_handler


app.include_router(APIRouter(route_class=LoggingRoute))
app.include_router(booking_router, prefix="/booking", tags=["booking"])

lambda_handler = Mangum(app)
