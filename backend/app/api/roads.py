"""
api/roads.py
------------
GET /roads -> list every Road node, together with the Junction it
belongs to (via the HAS_ROAD relationship).
"""

from fastapi import APIRouter
from app.services import traffic_service

router = APIRouter(prefix="/roads", tags=["Roads"])


@router.get("")
def list_roads():
    return traffic_service.get_all_roads()
