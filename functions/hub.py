from fastapi import FastAPI
from mangum import Mangum

from .routers import booking_router

app = FastAPI()

app.include_router(booking_router, prefix="/booking", tags=["booking"])

lambda_handler = Mangum(app)
