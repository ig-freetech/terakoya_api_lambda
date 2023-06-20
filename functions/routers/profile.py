import os
import sys
from typing import Any, Dict
from fastapi import APIRouter, Request, Depends

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(FUNCTIONS_DIR_PATH)

from functions.domain.authentication import authenticate_user

profile_router = APIRouter()


@profile_router.get("/profile")
def get_profile(request: Request, claims: Dict[str, Any] = Depends(authenticate_user)):
    return claims
