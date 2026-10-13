"""
api/junctions.py
-----------------
GET /junctions -> list every Junction node in Neo4j.
"""

from fastapi import APIRouter
from app.services import traffic_service

router = APIRouter(prefix="/junctions", tags=["Junctions"])


@router.get("")
def list_junctions():
    return traffic_service.get_all_junctions()
