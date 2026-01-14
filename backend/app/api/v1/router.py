from fastapi import APIRouter
from app.api.v1 import tests, reports, auth, learning, access_control

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(learning.router)  # Already has /learning prefix
api_router.include_router(access_control.router)  # Already has /access prefix

