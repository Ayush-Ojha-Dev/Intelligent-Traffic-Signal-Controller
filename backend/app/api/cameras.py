"""
api/cameras.py
---------------
GET /cameras -> list every Camera node, together with the Road it is
mounted on (via the HAS_CAMERA relationship).
"""

from fastapi import APIRouter
from app.services import traffic_service

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.get("")
def list_cameras():
    return traffic_service.get_all_cameras()
