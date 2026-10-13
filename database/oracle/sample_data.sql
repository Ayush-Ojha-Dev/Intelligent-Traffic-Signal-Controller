-- ============================================================
-- Intelligent Traffic Signal Controller
-- Sample Data
-- ============================================================


-- ============================================================
-- JUNCTION DATA
-- ============================================================

INSERT INTO JUNCTION (
    JunctionID,
    JunctionName,
    Location
)
VALUES (
    'J01',
    'Main Junction',
    'Chennai'
);


INSERT INTO JUNCTION (
    JunctionID,
    JunctionName,
    Location
)
VALUES (
    'J02',
    'College Junction',
    'Chennai'
);


-- ============================================================
-- ROAD DATA
-- ============================================================

INSERT INTO ROAD (
    RoadID,
    RoadName,
    Length,
    SpeedLimit,
    JunctionID
)
VALUES (
    'R01',
    'GST Road',
    2.50,
    60,
    'J01'
);


INSERT INTO ROAD (
    RoadID,
    RoadName,
    Length,
    SpeedLimit,
    JunctionID
)
VALUES (
    'R02',
    'OMR Road',
    3.20,
    50,
    'J01'
);


INSERT INTO ROAD (
    RoadID,
    RoadName,
    Length,
    SpeedLimit,
    JunctionID
)
VALUES (
    'R03',
    'College Road',
    1.80,
    40,
    'J02'
);


-- ============================================================
-- CAMERA DATA
-- ============================================================

INSERT INTO CAMERA (
    CameraID,
    RoadID,
    Location,
    Status
)
VALUES (
    'C01',
    'R01',
    'GST Road North',
    'ACTIVE'
);


INSERT INTO CAMERA (
    CameraID,
    RoadID,
    Location,
    Status
)
VALUES (
    'C02',
    'R02',
    'OMR Road East',
    'ACTIVE'
);


INSERT INTO CAMERA (
    CameraID,
    RoadID,
    Location,
    Status
)
VALUES (
    'C03',
    'R03',
    'College Road',
    'ACTIVE'
);


-- ============================================================
-- VEHICLE COUNT DATA
-- ============================================================

INSERT INTO VEHICLECOUNT (
    CameraID,
    VehicleCount,
    Density
)
VALUES (
    'C01',
    25,
    'LOW'
);


INSERT INTO VEHICLECOUNT (
    CameraID,
    VehicleCount,
    Density
)
VALUES (
    'C01',
    48,
    'MEDIUM'
);


INSERT INTO VEHICLECOUNT (
    CameraID,
    VehicleCount,
    Density
)
VALUES (
    'C02',
    75,
    'HIGH'
);


INSERT INTO VEHICLECOUNT (
    CameraID,
    VehicleCount,
    Density
)
VALUES (
    'C03',
    18,
    'LOW'
);


-- ============================================================
-- SIGNAL DATA
-- ============================================================

INSERT INTO SIGNAL (
    SignalID,
    JunctionID,
    SignalStatus,
    GreenTime,
    RedTime
)
VALUES (
    'S01',
    'J01',
    'GREEN',
    40,
    60
);


INSERT INTO SIGNAL (
    SignalID,
    JunctionID,
    SignalStatus,
    GreenTime,
    RedTime
)
VALUES (
    'S02',
    'J02',
    'RED',
    20,
    60
);


-- ============================================================
-- SAVE DATA
-- ============================================================

COMMIT;


-- ============================================================
-- VERIFICATION
-- ============================================================

SELECT 'JUNCTION' AS TABLE_NAME, COUNT(*) AS RECORD_COUNT
FROM JUNCTION

UNION ALL

SELECT 'ROAD', COUNT(*)
FROM ROAD

UNION ALL

SELECT 'CAMERA', COUNT(*)
FROM CAMERA

UNION ALL

SELECT 'VEHICLECOUNT', COUNT(*)
FROM VEHICLECOUNT

UNION ALL

SELECT 'SIGNAL', COUNT(*)
FROM SIGNAL;