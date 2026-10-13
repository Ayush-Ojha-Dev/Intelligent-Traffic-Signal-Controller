"""
services/signal_service.py
---------------------------
Pure, dependency-free business logic:

    vehicle_count  --> density  --> recommended_green_time

This is deliberately kept free of any database calls so it can be
tested/demoed instantly, even before Neo4j or Oracle are wired up.
Later, the equivalent logic will also exist as PL/SQL procedures
(calculate_density, calculate_signal_timing) for the Oracle side of
the project — this Python version is what the FastAPI backend uses at
request time; the PL/SQL version is for the relational-database
requirement and for generating congestion reports directly in Oracle.

Thresholds (from the project spec):

    Vehicle count      Density
    -------------      -------
    0  - 30            LOW
    31 - 60             MEDIUM
    61+                HIGH

    Density   Green time (sec)
    -------   ----------------
    LOW       20
    MEDIUM    40
    HIGH      60
"""

# Kept as module-level constants so the thresholds are easy to find and
# tune later (e.g. once real YOLO counts come in) without hunting
# through function bodies.
DENSITY_THRESHOLDS = {
    "LOW": (0, 30),
    "MEDIUM": (31, 60),
    # HIGH is anything above MEDIUM's upper bound (61+)
}

GREEN_TIME_BY_DENSITY = {
    "LOW": 20,
    "MEDIUM": 40,
    "HIGH": 60,
}


def calculate_density(vehicle_count: int) -> str:
    """Classify a vehicle count into LOW / MEDIUM / HIGH density."""
    if vehicle_count < 0:
        raise ValueError("vehicle_count cannot be negative")

    if vehicle_count <= 30:
        return "LOW"
    elif vehicle_count <= 60:
        return "MEDIUM"
    else:
        return "HIGH"


def calculate_green_time(density: str) -> int:
    """Map a density level to a recommended green-signal duration (sec)."""
    try:
        return GREEN_TIME_BY_DENSITY[density]
    except KeyError:
        raise ValueError(f"Unknown density level: {density!r}")


def process_vehicle_count(camera_id: str, vehicle_count: int) -> dict:
    """
    Convenience wrapper used by the API layer:
    vehicle_count -> density -> recommended_green_time, bundled into
    one dict ready to become a VehicleCountResponse.
    """
    density = calculate_density(vehicle_count)
    green_time = calculate_green_time(density)
    return {
        "camera_id": camera_id,
        "vehicle_count": vehicle_count,
        "density": density,
        "recommended_green_time": green_time,
    }
