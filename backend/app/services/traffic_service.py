
"""
services/traffic_service.py
---------------------------
Cypher queries and traffic-signal synchronization logic.

Graph model:
    (:Junction)-[:HAS_ROAD]->(:Road)
    (:Road)-[:HAS_CAMERA]->(:Camera)
    (:Camera)-[:RECORDS]->(:VehicleCount)
    (:Junction)-[:CONTROLS]->(:Signal)
"""

from app.database.neo4j import neo4j_conn
from app.services import oracle_service


# ---------------------------------------------------------------------
# Junction
# ---------------------------------------------------------------------
def get_all_junctions():
    query = """
    MATCH (j:Junction)
    RETURN j.junction_id AS junction_id,
           j.junction_name AS junction_name,
           j.location AS location
    ORDER BY j.junction_id
    """
    return neo4j_conn.run_query(query)


# ---------------------------------------------------------------------
# Road
# ---------------------------------------------------------------------
def get_all_roads():
    query = """
    MATCH (j:Junction)-[:HAS_ROAD]->(r:Road)
    RETURN r.road_id AS road_id,
           r.road_name AS road_name,
           r.length AS length,
           r.speed_limit AS speed_limit,
           j.junction_id AS junction_id
    ORDER BY r.road_id
    """
    return neo4j_conn.run_query(query)


# ---------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------
def get_all_cameras():
    query = """
    MATCH (r:Road)-[:HAS_CAMERA]->(c:Camera)
    RETURN c.camera_id AS camera_id,
           c.location AS location,
           c.status AS status,
           r.road_id AS road_id
    ORDER BY c.camera_id
    """
    return neo4j_conn.run_query(query)


# ---------------------------------------------------------------------
# Signal
# ---------------------------------------------------------------------
def get_all_signals():
    query = """
    MATCH (j:Junction)-[:CONTROLS]->(s:Signal)
    RETURN s.signal_id AS signal_id,
           s.signal_status AS signal_status,
           s.green_time AS green_time,
           s.red_time AS red_time,
           j.junction_id AS junction_id
    ORDER BY s.signal_id
    """
    return neo4j_conn.run_query(query)


def update_signal_timing(
    junction_id: str,
    green_time: int,
    red_time: int | None = None,
):
    """Update the existing Neo4j signal for a junction."""
    query = """
    MATCH (j:Junction {junction_id: $junction_id})
          -[:CONTROLS]->(s:Signal)
    SET s.green_time = $green_time,
        s.signal_status = 'GREEN'
    """

    params = {
        "junction_id": junction_id,
        "green_time": green_time,
    }

    if red_time is not None:
        query = """
        MATCH (j:Junction {junction_id: $junction_id})
              -[:CONTROLS]->(s:Signal)
        SET s.green_time = $green_time,
            s.red_time = $red_time,
            s.signal_status = 'GREEN'
        """
        params["red_time"] = red_time

    query += """
    RETURN
        j.junction_id AS junction_id,
        s.signal_id AS signal_id,
        s.signal_status AS signal_status,
        s.green_time AS green_time,
        s.red_time AS red_time
    """

    return neo4j_conn.run_query(query, params)


def sync_signal_from_oracle(junction_id: str):
    """
    Read a junction's signal from Oracle and synchronize Neo4j.

    Oracle is treated as the source of truth for signal timing.
    Returns None if Oracle or Neo4j has no matching signal.
    """
    oracle_signal = oracle_service.get_signal_for_junction(junction_id)

    if not oracle_signal:
        return None

    return update_signal_timing(
        junction_id=junction_id,
        green_time=int(oracle_signal["green_time"]),
        red_time=int(oracle_signal["red_time"]),
    )


def sync_all_signals_from_oracle():
    """Synchronize every Oracle signal to its matching Neo4j signal."""
    oracle_signals = oracle_service.get_signals()
    results = []

    for signal in oracle_signals:
        junction_id = signal["junction_id"]

        neo4j_result = update_signal_timing(
            junction_id=junction_id,
            green_time=int(signal["green_time"]),
            red_time=int(signal["red_time"]),
        )

        results.append({
            "junction_id": junction_id,
            "oracle_signal_id": signal["signal_id"],
            "synced": bool(neo4j_result),
            "neo4j": neo4j_result[0] if neo4j_result else None,
        })

    return results


# ---------------------------------------------------------------------
# VehicleCount
# ---------------------------------------------------------------------
def get_all_vehicle_counts():
    query = """
    MATCH (c:Camera)-[:RECORDS]->(vc:VehicleCount)
    RETURN vc.count_id AS count_id,
           vc.vehicle_count AS vehicle_count,
           vc.density AS density,
           vc.timestamp AS timestamp,
           c.camera_id AS camera_id
    ORDER BY vc.timestamp DESC
    """
    return neo4j_conn.run_query(query)


def save_vehicle_count(camera_id: str, vehicle_count: int, density: str):
    """
    Create a VehicleCount node linked to its Camera via RECORDS.
    """
    query = """
    MATCH (c:Camera {camera_id: $camera_id})
    CREATE (vc:VehicleCount {
        count_id: randomUUID(),
        vehicle_count: $vehicle_count,
        density: $density,
        timestamp: timestamp()
    })
    CREATE (c)-[:RECORDS]->(vc)
    RETURN vc.count_id AS count_id
    """

    params = {
        "camera_id": camera_id,
        "vehicle_count": vehicle_count,
        "density": density,
    }

    return neo4j_conn.run_query(query, params)


def get_junction_for_camera(camera_id: str):
    query = """
    MATCH (j:Junction)-[:HAS_ROAD]->(r:Road)-[:HAS_CAMERA]->(c:Camera)
    WHERE c.camera_id = $camera_id
    RETURN j.junction_id AS junction_id
    """

    result = neo4j_conn.run_query(query, {"camera_id": camera_id})

    if not result:
        return None

    return result[0]["junction_id"]


# ---------------------------------------------------------------------
# Emergency priority simulation
# ---------------------------------------------------------------------
def set_emergency_priority(junction_id: str, green_time: int = 90):
    """
    Update an existing Neo4j signal for emergency-priority simulation.

    This function updates the database only; it does not control
    physical traffic-light hardware.
    """
    query = """
    MATCH (j:Junction {junction_id: $junction_id})
          -[:CONTROLS]->(s:Signal)
    SET s.signal_status = 'GREEN',
        s.green_time = $green_time
    RETURN
        j.junction_id AS junction_id,
        s.signal_id AS signal_id,
        s.signal_status AS signal_status,
        s.green_time AS green_time,
        s.red_time AS red_time
    """

    return neo4j_conn.run_query(
        query,
        {
            "junction_id": junction_id,
            "green_time": green_time,
        },
    )
