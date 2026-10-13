
"""
api/signals.py
--------------
Signal listing, emergency-priority, and synchronization endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import oracle_service, traffic_service

router = APIRouter(prefix="/signals", tags=["Signals"])


class EmergencyPriorityRequest(BaseModel):
    junction_id: str = Field(..., example="J01")
    green_time: int = Field(default=90, ge=1, le=180)


@router.get("")
def list_signals():
    """List all signals from Neo4j."""
    return traffic_service.get_all_signals()


@router.post("/emergency-priority")
def emergency_priority(payload: EmergencyPriorityRequest):
    """Apply emergency priority to both database simulations."""

    oracle_signal = oracle_service.get_signal_for_junction(
        payload.junction_id
    )

    if not oracle_signal:
        raise HTTPException(
            status_code=404,
            detail=f"No signal found in Oracle for junction '{payload.junction_id}'",
        )

    updated_signal = oracle_service.set_emergency_priority(
        junction_id=payload.junction_id,
        green_time=payload.green_time,
    )

    if not updated_signal:
        raise HTTPException(
            status_code=500,
            detail="Oracle did not return the updated signal.",
        )

    try:
        neo4j_result = traffic_service.sync_signal_from_oracle(
            payload.junction_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Oracle was updated, but Neo4j sync failed: {exc}",
        )

    if not neo4j_result:
        raise HTTPException(
            status_code=500,
            detail="Oracle was updated, but no matching Neo4j signal was found.",
        )

    return {
        "message": "Emergency priority applied and synchronized",
        "oracle": updated_signal,
        "neo4j": neo4j_result[0],
    }


@router.post("/synchronize")
def synchronize_signals():
    """
    Synchronize all existing Oracle signal timings to Neo4j.
    Oracle is treated as the source of truth.
    """
    try:
        results = traffic_service.sync_all_signals_from_oracle()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Signal synchronization failed: {exc}",
        )

    failed = [item for item in results if not item["synced"]]

    return {
        "message": (
            "Synchronization completed"
            if not failed
            else "Synchronization completed with failures"
        ),
        "total": len(results),
        "successful": len(results) - len(failed),
        "failed": failed,
        "results": results,
    }
