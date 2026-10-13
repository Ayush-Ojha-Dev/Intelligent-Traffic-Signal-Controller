
from fastapi import APIRouter
from app.database.neo4j import neo4j_conn

router = APIRouter(prefix="/traffic", tags=["Traffic Reports"])


@router.get("/congestion-report")
def congestion_report():
    query = """
    MATCH (j:Junction)-[:HAS_ROAD]->(r:Road)-[:HAS_CAMERA]->(c:Camera)
    OPTIONAL MATCH (c)-[:RECORDS]->(vc:VehicleCount)
    WITH j, r, c, vc
    ORDER BY vc.timestamp DESC
    WITH j, r, c, collect(vc)[0] AS latest
    RETURN
        j.junction_id AS junction_id,
        j.junction_name AS junction_name,
        r.road_id AS road_id,
        r.road_name AS road_name,
        c.camera_id AS camera_id,
        latest.vehicle_count AS vehicle_count,
        latest.density AS density,
        latest.timestamp AS timestamp
    ORDER BY j.junction_id, c.camera_id
    """
    return neo4j_conn.run_query(query)
