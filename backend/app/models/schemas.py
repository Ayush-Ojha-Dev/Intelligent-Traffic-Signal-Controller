"""
models/schemas.py
------------------
Pydantic models describing the shape of data flowing in and out of the
API. These mirror the 5 approved entities (Junction, Road, Camera,
VehicleCount, Signal) — no extra entities such as EmergencyVehicle are
introduced here, in line with the project's entity restriction.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ---------------------------------------------------------------------
# Junction
# ---------------------------------------------------------------------
class Junction(BaseModel):
    junction_id: str
    junction_name: str
    location: Optional[str] = None


# ---------------------------------------------------------------------
# Road
# ---------------------------------------------------------------------
class Road(BaseModel):
    road_id: str
    road_name: str
    length: Optional[float] = None
    speed_limit: Optional[float] = None
    junction_id: Optional[str] = None  # the junction this road belongs to


# ---------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------
class Camera(BaseModel):
    camera_id: str
    road_id: str
    location: Optional[str] = None
    status: Optional[str] = "ACTIVE"


# ---------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------
class Signal(BaseModel):
    signal_id: str
    junction_id: str
    signal_status: Optional[str] = "RED"
    green_time: Optional[int] = None
    red_time: Optional[int] = None


# ---------------------------------------------------------------------
# VehicleCount — request coming FROM a camera / detection script
# ---------------------------------------------------------------------
class VehicleCountRequest(BaseModel):
    camera_id: str = Field(..., example="C01")
    vehicle_count: int = Field(..., ge=0, example=72)


# ---------------------------------------------------------------------
# VehicleCount — response sent back TO the caller after processing
# ---------------------------------------------------------------------
class VehicleCountResponse(BaseModel):
    camera_id: str
    vehicle_count: int
    density: str
    recommended_green_time: int
