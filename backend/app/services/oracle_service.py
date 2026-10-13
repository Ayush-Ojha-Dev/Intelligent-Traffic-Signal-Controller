"""
services/oracle_service.py

Oracle database operations for the
Intelligent Traffic Signal Controller.

This service communicates with the Oracle database
and uses the PL/SQL functions/procedures created
for the project.
"""

from app.database.oracle import oracle_conn


def save_vehicle_count(
    camera_id: str,
    vehicle_count: int,
    density: str
):
    """
    Save a vehicle-count reading into Oracle.
    """

    query = """
        INSERT INTO VEHICLECOUNT (
            CameraID,
            VehicleCount,
            Density
        )
        VALUES (
            :camera_id,
            :vehicle_count,
            :density
        )
    """

    params = {
        "camera_id": camera_id,
        "vehicle_count": vehicle_count,
        "density": density,
    }

    oracle_conn.execute(query, params)


def update_signal_timing(camera_id: str):
    """
    Call the PL/SQL procedure that calculates
    traffic density and updates signal timing.
    """

    statement = """
        BEGIN
            update_signal_timing(:camera_id);
        END;
    """

    params = {
        "camera_id": camera_id,
    }

    oracle_conn.execute_plsql(statement, params)


def get_vehicle_counts():
    """
    Retrieve vehicle-count records from Oracle.
    """

    query = """
        SELECT
            vc.CountID AS count_id,
            vc.CameraID AS camera_id,
            vc.VehicleCount AS vehicle_count,
            vc.Timestamp AS timestamp,
            vc.Density AS density
        FROM VEHICLECOUNT vc
        ORDER BY vc.Timestamp DESC
    """

    return oracle_conn.fetch_all(query)


def get_signals():
    """
    Retrieve signal information from Oracle.
    """

    query = """
        SELECT
            SignalID AS signal_id,
            JunctionID AS junction_id,
            SignalStatus AS signal_status,
            GreenTime AS green_time,
            RedTime AS red_time
        FROM SIGNAL
        ORDER BY SignalID
    """

    return oracle_conn.fetch_all(query)


def get_cameras():
    """
    Retrieve camera information from Oracle.
    """

    query = """
        SELECT
            CameraID AS camera_id,
            RoadID AS road_id,
            Location AS location,
            Status AS status
        FROM CAMERA
        ORDER BY CameraID
    """

    return oracle_conn.fetch_all(query)


def get_signal_for_junction(junction_id: str):
    """
    Retrieve the signal timing for a specific junction from Oracle.
    """
    query = """
        SELECT
            SignalID AS signal_id,
            JunctionID AS junction_id,
            SignalStatus AS signal_status,
            GreenTime AS green_time,
            RedTime AS red_time
        FROM SIGNAL
        WHERE JunctionID = :junction_id
    """

    result = oracle_conn.fetch_all(
        query,
        {"junction_id": junction_id}
    )

    return result[0] if result else None
def set_emergency_priority(junction_id: str, green_time: int = 90):
    """
    Apply emergency priority to the existing Oracle signal record.
    This updates the database simulation, not physical traffic lights.
    """
    query = """
        UPDATE SIGNAL
        SET SignalStatus = 'GREEN',
            GreenTime = :green_time
        WHERE JunctionID = :junction_id
    """

    oracle_conn.execute(
        query,
        {
            "green_time": green_time,
            "junction_id": junction_id,
        },
    )

    return get_signal_for_junction(junction_id)
