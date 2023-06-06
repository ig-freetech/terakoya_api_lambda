from fastapi import FastAPI, APIRouter, Request
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from typing import Callable

from .routers import booking_router

app = FastAPI()

app.include_router(booking_router, prefix="/booking", tags=["booking"])

# FastAPI restricts OPTIONS requests (preflight requests) by default, so even if you allow them on the API Gateway side, if you do not allow them on the FastAPI side, a 405 error will be returned.
# So, you need to explicitly include CORS headers in the response in FastAPI middleware so that the browser can make preflight requests.
# https://fastapi.tiangolo.com/ja/tutorial/cors/
# https://developer.mozilla.org/ja/docs/Web/HTTP/Status/405
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

lambda_handler = Mangum(app)
