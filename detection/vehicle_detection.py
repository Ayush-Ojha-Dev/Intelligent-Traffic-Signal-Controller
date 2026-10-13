"""
detection/vehicle_detection.py
--------------------------------
Placeholder for the later computer-vision stage of the project.

For the FIRST REVIEW, this file is NOT required to run — the backend
is demoed with dummy vehicle counts sent straight to
POST /vehicle-counts. This script is here only so the folder
structure and pipeline are visible end-to-end, and so the later
integration step is a small, well-scoped change instead of a new
subsystem.

Planned pipeline (post first-review):

    Camera frame/video
        -> OpenCV read
        -> YOLOv8 inference (car / bike / bus / truck classes)
        -> count detections
        -> POST http://localhost:8000/vehicle-counts
               {"camera_id": ..., "vehicle_count": ...}

Intentionally left unimplemented until the basic backend
(this repo's backend/ folder) is verified working with dummy data.
"""

import requests

API_URL = "http://localhost:8000/vehicle-counts"


def send_vehicle_count(camera_id: str, vehicle_count: int):
    """
    Minimal helper that will eventually be called once per processed
    frame/video-segment, after YOLO produces a vehicle_count for a
    given camera_id. Kept here (rather than inline in the YOLO loop)
    so the HTTP call is easy to test on its own with dummy numbers.
    """
    response = requests.post(
        API_URL,
        json={"camera_id": camera_id, "vehicle_count": vehicle_count},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    # Quick manual smoke test using a dummy count -- replace with
    # real YOLO output once OpenCV/YOLO integration begins.
    result = send_vehicle_count(camera_id="C01", vehicle_count=45)
    print(result)
