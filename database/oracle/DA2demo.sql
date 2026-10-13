-- ============================================================
-- INTELLIGENT TRAFFIC SIGNAL CONTROLLER
-- DA2 DEMONSTRATION SCRIPT
--
-- SQL + PL/SQL
--
-- Entities:
-- 1. JUNCTION
-- 2. ROAD
-- 3. CAMERA
-- 4. VEHICLECOUNT
-- 5. SIGNAL
-- ============================================================


SET SERVEROUTPUT ON;
SET LINESIZE 150;
SET PAGESIZE 100;


-- ============================================================
-- 1. DISPLAY ALL JUNCTIONS
-- ============================================================

PROMPT ==========================================
PROMPT 1. JUNCTION DETAILS
PROMPT ==========================================

SELECT
    JunctionID,
    JunctionName,
    Location
FROM JUNCTION
ORDER BY JunctionID;


-- ============================================================
-- 2. DISPLAY ALL ROADS
-- ============================================================

PROMPT ==========================================
PROMPT 2. ROAD DETAILS
PROMPT ==========================================

SELECT
    r.RoadID,
    r.RoadName,
    r.Length,
    r.SpeedLimit,
    j.JunctionName
FROM ROAD r
JOIN JUNCTION j
    ON r.JunctionID = j.JunctionID
ORDER BY r.RoadID;


-- ============================================================
-- 3. DISPLAY CAMERA INFORMATION
-- ============================================================

PROMPT ==========================================
PROMPT 3. CAMERA DETAILS
PROMPT ==========================================

SELECT
    c.CameraID,
    c.Location,
    c.Status,
    r.RoadName
FROM CAMERA c
JOIN ROAD r
    ON c.RoadID = r.RoadID
ORDER BY c.CameraID;


-- ============================================================
-- 4. DISPLAY SIGNAL INFORMATION
-- ============================================================

PROMPT ==========================================
PROMPT 4. SIGNAL DETAILS
PROMPT ==========================================

SELECT
    s.SignalID,
    j.JunctionName,
    s.SignalStatus,
    s.GreenTime,
    s.RedTime
FROM SIGNAL s
JOIN JUNCTION j
    ON s.JunctionID = j.JunctionID
ORDER BY s.SignalID;


-- ============================================================
-- 5. DISPLAY VEHICLE COUNTS
-- ============================================================

PROMPT ==========================================
PROMPT 5. VEHICLE COUNT DETAILS
PROMPT ==========================================

SELECT
    vc.CountID,
    vc.CameraID,
    vc.VehicleCount,
    vc.Density,
    vc.Timestamp
FROM VEHICLECOUNT vc
ORDER BY vc.Timestamp DESC;


-- ============================================================
-- 6. MULTI-TABLE JOIN
--
-- Junction -> Road -> Camera -> VehicleCount
-- ============================================================

PROMPT ==========================================
PROMPT 6. COMPLETE TRAFFIC INFORMATION
PROMPT ==========================================

SELECT
    j.JunctionName,
    r.RoadName,
    c.CameraID,
    vc.VehicleCount,
    vc.Density,
    vc.Timestamp
FROM JUNCTION j
JOIN ROAD r
    ON j.JunctionID = r.JunctionID
JOIN CAMERA c
    ON r.RoadID = c.RoadID
JOIN VEHICLECOUNT vc
    ON c.CameraID = vc.CameraID
ORDER BY vc.Timestamp DESC;


-- ============================================================
-- 7. AGGREGATE QUERY
--
-- Average vehicle count for every camera
-- ============================================================

PROMPT ==========================================
PROMPT 7. AVERAGE VEHICLE COUNT BY CAMERA
PROMPT ==========================================

SELECT
    CameraID,
    COUNT(*) AS NumberOfReadings,
    ROUND(AVG(VehicleCount), 2) AS AverageVehicles,
    MAX(VehicleCount) AS MaximumVehicles
FROM VEHICLECOUNT
GROUP BY CameraID
ORDER BY CameraID;


-- ============================================================
-- 8. HIGH-DENSITY TRAFFIC
-- ============================================================

PROMPT ==========================================
PROMPT 8. HIGH-DENSITY TRAFFIC
PROMPT ==========================================

SELECT
    vc.CameraID,
    c.Location,
    vc.VehicleCount,
    vc.Density,
    vc.Timestamp
FROM VEHICLECOUNT vc
JOIN CAMERA c
    ON vc.CameraID = c.CameraID
WHERE vc.Density = 'HIGH'
ORDER BY vc.VehicleCount DESC;


-- ============================================================
-- 9. TRAFFIC DENSITY DISTRIBUTION
-- ============================================================

PROMPT ==========================================
PROMPT 9. TRAFFIC DENSITY DISTRIBUTION
PROMPT ==========================================

SELECT
    Density,
    COUNT(*) AS ReadingCount
FROM VEHICLECOUNT
GROUP BY Density
ORDER BY Density;


-- ============================================================
-- 10. SQL UPDATE DEMONSTRATION
--
-- Change C03 camera status temporarily.
-- ROLLBACK is used so the original data remains unchanged.
-- ============================================================

PROMPT ==========================================
PROMPT 10. UPDATE OPERATION
PROMPT ==========================================

UPDATE CAMERA
SET Status = 'MAINTENANCE'
WHERE CameraID = 'C03';

SELECT
    CameraID,
    Status
FROM CAMERA
WHERE CameraID = 'C03';

ROLLBACK;

SELECT
    CameraID,
    Status
FROM CAMERA
WHERE CameraID = 'C03';


-- ============================================================
-- 11. SQL INSERT DEMONSTRATION
--
-- Use a SAVEPOINT and ROLLBACK so no extra sample
-- record remains permanently in the database.
-- ============================================================

PROMPT ==========================================
PROMPT 11. INSERT OPERATION
PROMPT ==========================================

SAVEPOINT before_demo_insert;

INSERT INTO VEHICLECOUNT (
    CameraID,
    VehicleCount,
    Density
)
VALUES (
    'C03',
    35,
    'MEDIUM'
);

SELECT
    CameraID,
    VehicleCount,
    Density
FROM VEHICLECOUNT
WHERE CameraID = 'C03'
ORDER BY Timestamp DESC;

ROLLBACK TO before_demo_insert;


-- ============================================================
-- 12. PL/SQL DENSITY FUNCTION
-- ============================================================

PROMPT ==========================================
PROMPT 12. PL/SQL DENSITY FUNCTION
PROMPT ==========================================

SELECT
    calculate_density(25) AS Density_Low
FROM dual;

SELECT
    calculate_density(48) AS Density_Medium
FROM dual;

SELECT
    calculate_density(75) AS Density_High
FROM dual;


-- ============================================================
-- 13. PL/SQL GREEN-TIME FUNCTION
-- ============================================================

PROMPT ==========================================
PROMPT 13. PL/SQL GREEN-TIME FUNCTION
PROMPT ==========================================

SELECT
    calculate_green_time('LOW') AS GreenTime_Low
FROM dual;

SELECT
    calculate_green_time('MEDIUM') AS GreenTime_Medium
FROM dual;

SELECT
    calculate_green_time('HIGH') AS GreenTime_High
FROM dual;


-- ============================================================
-- 14. PL/SQL SIGNAL TIMING PROCEDURE
--
-- C02 currently has high traffic.
-- ============================================================

PROMPT ==========================================
PROMPT 14. PL/SQL SIGNAL TIMING UPDATE
PROMPT ==========================================

EXEC update_signal_timing('C02');


-- ============================================================
-- 15. VERIFY SIGNAL TIMING AFTER PL/SQL UPDATE
-- ============================================================

PROMPT ==========================================
PROMPT 15. UPDATED SIGNAL
PROMPT ==========================================

SELECT
    SignalID,
    JunctionID,
    SignalStatus,
    GreenTime,
    RedTime
FROM SIGNAL
WHERE JunctionID = 'J01';


-- ============================================================
-- 16. PL/SQL CONGESTION REPORT
-- ============================================================

PROMPT ==========================================
PROMPT 16. CONGESTION REPORT
PROMPT ==========================================

EXEC congestion_report;


-- ============================================================
-- 17. PL/SQL EMERGENCY PRIORITY
--
-- Emergency priority is implemented as a procedure,
-- NOT as a separate database entity.
-- ============================================================

PROMPT ==========================================
PROMPT 17. EMERGENCY PRIORITY
PROMPT ==========================================

EXEC emergency_priority('J01');


-- ============================================================
-- 18. VERIFY EMERGENCY PRIORITY SIGNAL
-- ============================================================

PROMPT ==========================================
PROMPT 18. SIGNAL AFTER EMERGENCY PRIORITY
PROMPT ==========================================

SELECT
    SignalID,
    JunctionID,
    SignalStatus,
    GreenTime,
    RedTime
FROM SIGNAL
WHERE JunctionID = 'J01';


-- ============================================================
-- END OF DEMONSTRATION
-- ============================================================

PROMPT ==========================================
PROMPT DA2 DEMONSTRATION COMPLETED
PROMPT ==========================================
