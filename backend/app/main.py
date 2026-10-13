
"""
main.py
-------
FastAPI application entry point for the Intelligent Traffic Signal
Controller backend.

Run from the backend/ folder:
    uvicorn app.main:app --reload

Swagger documentation:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

from app.config import settings
from app.api import (
    junctions,
    roads,
    cameras,
    vehicle_counts,
    signals,
    traffic,
)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend for the Intelligent Traffic Signal Controller "
        "mini-project."
    ),
    version="0.1.0",
)


@app.get("/", tags=["Health"])
def root():
    """Simple health-check / welcome route."""
    return {
        "message": f"{settings.APP_NAME} backend is running.",
        "env": settings.ENV,
        "docs": "/docs",
    }


# Register entity routers.
app.include_router(junctions.router)
app.include_router(roads.router)
app.include_router(cameras.router)
app.include_router(signals.router)
app.include_router(vehicle_counts.router)

# Register traffic reporting routes.
app.include_router(traffic.router)
