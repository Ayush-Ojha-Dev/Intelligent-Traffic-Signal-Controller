
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------
# Vehicle-count API tests
# ---------------------------------------------------------

@patch("app.api.vehicle_counts.traffic_service.get_junction_for_camera")
@patch("app.api.vehicle_counts.traffic_service.save_vehicle_count")
@patch("app.api.vehicle_counts.oracle_service.save_vehicle_count")
@patch("app.api.vehicle_counts.oracle_service.update_signal_timing")
@patch("app.api.vehicle_counts.traffic_service.sync_signal_from_oracle")
def test_create_vehicle_count_low_density(
    mock_sync,
    mock_update_timing,
    mock_oracle_save,
    mock_neo4j_save,
    mock_get_junction,
):
    mock_get_junction.return_value = "J01"
    mock_neo4j_save.return_value = [{"count_id": "test-count"}]
    mock_sync.return_value = [
        {
            "junction_id": "J01",
            "signal_id": "S01",
            "green_time": 20,
            "red_time": 60,
        }
    ]

    response = client.post(
        "/vehicle-counts",
        json={"camera_id": "C01", "vehicle_count": 20},
    )

    assert response.status_code == 200
    assert response.json() == {
        "camera_id": "C01",
        "vehicle_count": 20,
        "density": "LOW",
        "recommended_green_time": 20,
    }

    mock_neo4j_save.assert_called_once()
    mock_oracle_save.assert_called_once()
    mock_update_timing.assert_called_once_with(camera_id="C01")
    mock_sync.assert_called_once_with("J01")


def test_create_vehicle_count_rejects_negative_count():
    response = client.post(
        "/vehicle-counts",
        json={"camera_id": "C01", "vehicle_count": -1},
    )

    assert response.status_code == 422


def test_create_vehicle_count_rejects_missing_camera_id():
    response = client.post(
        "/vehicle-counts",
        json={"vehicle_count": 20},
    )

    assert response.status_code == 422


@patch("app.api.vehicle_counts.traffic_service.get_junction_for_camera")
def test_create_vehicle_count_returns_404_for_unknown_camera(
    mock_get_junction,
):
    mock_get_junction.return_value = None

    response = client.post(
        "/vehicle-counts",
        json={"camera_id": "UNKNOWN", "vehicle_count": 20},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------
# Emergency-priority API tests
# ---------------------------------------------------------

@patch("app.api.signals.traffic_service.sync_signal_from_oracle")
@patch("app.api.signals.oracle_service.set_emergency_priority")
@patch("app.api.signals.oracle_service.get_signal_for_junction")
def test_emergency_priority_updates_and_syncs_signal(
    mock_get_signal,
    mock_set_priority,
    mock_sync,
):
    mock_get_signal.return_value = {
        "signal_id": "S02",
        "junction_id": "J02",
        "signal_status": "GREEN",
        "green_time": 20,
        "red_time": 60,
    }

    mock_set_priority.return_value = {
        "signal_id": "S02",
        "junction_id": "J02",
        "signal_status": "GREEN",
        "green_time": 90,
        "red_time": 60,
    }

    mock_sync.return_value = [
        {
            "junction_id": "J02",
            "signal_id": "S02",
            "signal_status": "GREEN",
            "green_time": 90,
            "red_time": 60,
        }
    ]

    response = client.post(
        "/signals/emergency-priority",
        json={"junction_id": "J02", "green_time": 90},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["oracle"]["green_time"] == 90
    assert body["neo4j"]["green_time"] == 90
    assert body["oracle"]["junction_id"] == "J02"
    assert body["neo4j"]["junction_id"] == "J02"

    mock_set_priority.assert_called_once_with(
        junction_id="J02",
        green_time=90,
    )
    mock_sync.assert_called_once_with("J02")


@patch("app.api.signals.oracle_service.get_signal_for_junction")
def test_emergency_priority_returns_404_for_unknown_junction(
    mock_get_signal,
):
    mock_get_signal.return_value = None

    response = client.post(
        "/signals/emergency-priority",
        json={"junction_id": "UNKNOWN", "green_time": 90},
    )

    assert response.status_code == 404


def test_emergency_priority_rejects_invalid_green_time():
    response = client.post(
        "/signals/emergency-priority",
        json={"junction_id": "J02", "green_time": 0},
    )

    assert response.status_code == 422


@patch("app.api.signals.traffic_service.sync_signal_from_oracle")
@patch("app.api.signals.oracle_service.set_emergency_priority")
@patch("app.api.signals.oracle_service.get_signal_for_junction")
def test_emergency_priority_reports_sync_failure(
    mock_get_signal,
    mock_set_priority,
    mock_sync,
):
    mock_get_signal.return_value = {
        "signal_id": "S02",
        "junction_id": "J02",
        "signal_status": "GREEN",
        "green_time": 20,
        "red_time": 60,
    }

    mock_set_priority.return_value = {
        "signal_id": "S02",
        "junction_id": "J02",
        "signal_status": "GREEN",
        "green_time": 90,
        "red_time": 60,
    }

    mock_sync.return_value = None

    response = client.post(
        "/signals/emergency-priority",
        json={"junction_id": "J02", "green_time": 90},
    )

    assert response.status_code == 500
    assert "Neo4j" in response.json()["detail"]


# ---------------------------------------------------------
# Signal synchronization API tests
# ---------------------------------------------------------

@patch("app.api.signals.traffic_service.sync_all_signals_from_oracle")
def test_synchronize_signals_success(mock_sync_all):
    mock_sync_all.return_value = [
        {
            "junction_id": "J01",
            "oracle_signal_id": "S01",
            "synced": True,
            "neo4j": {
                "junction_id": "J01",
                "signal_id": "S01",
                "signal_status": "GREEN",
                "green_time": 20,
                "red_time": 60,
            },
        },
        {
            "junction_id": "J02",
            "oracle_signal_id": "S02",
            "synced": True,
            "neo4j": {
                "junction_id": "J02",
                "signal_id": "S02",
                "signal_status": "GREEN",
                "green_time": 40,
                "red_time": 60,
            },
        },
    ]

    response = client.post("/signals/synchronize")

    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 2
    assert body["successful"] == 2
    assert body["failed"] == []
    assert body["message"] == "Synchronization completed"

    mock_sync_all.assert_called_once_with()


@patch("app.api.signals.traffic_service.sync_all_signals_from_oracle")
def test_synchronize_signals_reports_partial_failure(mock_sync_all):
    mock_sync_all.return_value = [
        {
            "junction_id": "J01",
            "oracle_signal_id": "S01",
            "synced": True,
            "neo4j": {
                "junction_id": "J01",
                "signal_id": "S01",
                "signal_status": "GREEN",
                "green_time": 20,
                "red_time": 60,
            },
        },
        {
            "junction_id": "J02",
            "oracle_signal_id": "S02",
            "synced": False,
            "neo4j": None,
        },
    ]

    response = client.post("/signals/synchronize")

    assert response.status_code == 200

    body = response.json()
    assert body["total"] == 2
    assert body["successful"] == 1
    assert len(body["failed"]) == 1
    assert body["failed"][0]["junction_id"] == "J02"
    assert body["message"] == "Synchronization completed with failures"


@patch("app.api.signals.traffic_service.sync_all_signals_from_oracle")
def test_synchronize_signals_handles_exception(mock_sync_all):
    mock_sync_all.side_effect = RuntimeError("Database unavailable")

    response = client.post("/signals/synchronize")

    assert response.status_code == 500
    assert "Database unavailable" in response.json()["detail"]
