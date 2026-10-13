
"""
api/vehicle_counts.py
---------------------
Vehicle-count API routes.

Flow:
1. Calculate traffic density.
2. Verify the camera and its junction exist in Neo4j.
3. Save the vehicle count in Neo4j and Oracle.
4. Call Oracle PL/SQL to update signal timing.
5. Synchronize the signal from Oracle to Neo4j.
6. Return the vehicle-count result.
"""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    VehicleCountRequest,
    VehicleCountResponse,
)

from app.services import (
    signal_service,
    traffic_service,
    oracle_service,
)


router = APIRouter(
    prefix="/vehicle-counts",
    tags=["Vehicle Counts"],
)


@router.get("")
def list_vehicle_counts():
    """Return vehicle-count records from Neo4j."""
    return traffic_service.get_all_vehicle_counts()


@router.post(
    "",
    response_model=VehicleCountResponse,
)
def create_vehicle_count(
    payload: VehicleCountRequest,
):
    """
    Process a new vehicle-count reading.

    The reading is stored in Neo4j and Oracle.
    Oracle PL/SQL calculates the signal timing, and the
    resulting signal timing is synchronized to Neo4j.
    """

    # 1. Calculate density and recommended green time.
    result = signal_service.process_vehicle_count(
        camera_id=payload.camera_id,
        vehicle_count=payload.vehicle_count,
    )

    # 2. Verify that the camera exists and find its junction.
    junction_id = traffic_service.get_junction_for_camera(
        payload.camera_id
    )

    if junction_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"Camera '{payload.camera_id}' not found",
        )

    # 3. Save the vehicle count in Neo4j.
    neo4j_saved = traffic_service.save_vehicle_count(
        camera_id=payload.camera_id,
        vehicle_count=payload.vehicle_count,
        density=result["density"],
    )

    if not neo4j_saved:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Could not save vehicle count: camera "
                f"'{payload.camera_id}' was not found in Neo4j"
            ),
        )

    # 4. Save the count and run Oracle PL/SQL.
    try:
        oracle_service.save_vehicle_count(
            camera_id=payload.camera_id,
            vehicle_count=payload.vehicle_count,
            density=result["density"],
        )

        # 5. Let Oracle calculate and update signal timing.
        oracle_service.update_signal_timing(
            camera_id=payload.camera_id
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Oracle operation failed: {str(exc)}",
        )

    # 6. Synchronize the updated Oracle signal to Neo4j.
    try:
        synced_signal = traffic_service.sync_signal_from_oracle(
            junction_id
        )

        if not synced_signal:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"Oracle timing was updated, but no matching "
                    f"signal was found in Neo4j for junction "
                    f"'{junction_id}'"
                ),
            )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                "Oracle timing was updated, but synchronization "
                f"to Neo4j failed: {str(exc)}"
            ),
        )

    # 7. Return the vehicle-count calculation.
    return result
