
import pytest

from app.services.signal_service import (
    calculate_density,
    calculate_green_time,
    process_vehicle_count,
)


@pytest.mark.parametrize(
    ("vehicle_count", "expected_density"),
    [
        (0, "LOW"),
        (1, "LOW"),
        (30, "LOW"),
        (31, "MEDIUM"),
        (45, "MEDIUM"),
        (60, "MEDIUM"),
        (61, "HIGH"),
        (100, "HIGH"),
    ],
)
def test_calculate_density(vehicle_count, expected_density):
    assert calculate_density(vehicle_count) == expected_density


def test_negative_vehicle_count_raises_error():
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_density(-1)


@pytest.mark.parametrize(
    ("density", "expected_green_time"),
    [
        ("LOW", 20),
        ("MEDIUM", 40),
        ("HIGH", 60),
    ],
)
def test_calculate_green_time(density, expected_green_time):
    assert calculate_green_time(density) == expected_green_time


def test_unknown_density_raises_error():
    with pytest.raises(ValueError, match="Unknown density level"):
        calculate_green_time("UNKNOWN")


def test_process_vehicle_count():
    result = process_vehicle_count("C01", 45)

    assert result == {
        "camera_id": "C01",
        "vehicle_count": 45,
        "density": "MEDIUM",
        "recommended_green_time": 40,
    }
