-- ============================================================
-- Intelligent Traffic Signal Controller
-- PL/SQL Procedures and Functions
--
-- Required features:
-- 1. Traffic Density
-- 2. Signal Timing
-- 3. Congestion Report
-- 4. Emergency Priority
--
-- Emergency Priority is implemented as a procedure/feature.
-- It is NOT a separate database entity.
-- ============================================================


-- ============================================================
-- 1. FUNCTION: CALCULATE TRAFFIC DENSITY
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_density (
    p_vehicle_count IN NUMBER
)
RETURN VARCHAR2
IS
BEGIN

    IF p_vehicle_count < 0 THEN

        RAISE_APPLICATION_ERROR(
            -20001,
            'Vehicle count cannot be negative'
        );

    ELSIF p_vehicle_count <= 30 THEN

        RETURN 'LOW';

    ELSIF p_vehicle_count <= 60 THEN

        RETURN 'MEDIUM';

    ELSE

        RETURN 'HIGH';

    END IF;

END calculate_density;
/
SHOW ERRORS FUNCTION calculate_density;


-- ============================================================
-- 2. FUNCTION: CALCULATE SIGNAL GREEN TIME
-- ============================================================

CREATE OR REPLACE FUNCTION calculate_green_time (
    p_density IN VARCHAR2
)
RETURN NUMBER
IS
    v_density VARCHAR2(20);
BEGIN

    v_density := UPPER(TRIM(p_density));

    IF v_density = 'LOW' THEN

        RETURN 20;

    ELSIF v_density = 'MEDIUM' THEN

        RETURN 40;

    ELSIF v_density = 'HIGH' THEN

        RETURN 60;

    ELSE

        RAISE_APPLICATION_ERROR(
            -20002,
            'Invalid density. Use LOW, MEDIUM or HIGH.'
        );

    END IF;

END calculate_green_time;
/
SHOW ERRORS FUNCTION calculate_green_time;


-- ============================================================
-- 3. PROCEDURE: UPDATE SIGNAL TIMING
--
-- Finds the latest vehicle count for a camera, calculates
-- density and green time, then updates the signal associated
-- with that camera's junction.
-- ============================================================

CREATE OR REPLACE PROCEDURE update_signal_timing (
    p_camera_id IN VARCHAR2
)
IS

    v_vehicle_count VEHICLECOUNT.VehicleCount%TYPE;
    v_density       VEHICLECOUNT.Density%TYPE;
    v_green_time    SIGNAL.GreenTime%TYPE;
    v_junction_id   JUNCTION.JunctionID%TYPE;

BEGIN

    -- Find the latest vehicle count for the camera.

    SELECT VehicleCount
    INTO v_vehicle_count
    FROM (
        SELECT VehicleCount
        FROM VEHICLECOUNT
        WHERE CameraID = p_camera_id
        ORDER BY Timestamp DESC, CountID DESC
    )
    WHERE ROWNUM = 1;


    -- Calculate traffic density.

    v_density := calculate_density(v_vehicle_count);


    -- Calculate recommended green time.

    v_green_time := calculate_green_time(v_density);


    -- Find the junction associated with the camera.

    SELECT r.JunctionID
    INTO v_junction_id
    FROM CAMERA c
    JOIN ROAD r
        ON c.RoadID = r.RoadID
    WHERE c.CameraID = p_camera_id;


    -- Update the signal controlled by the junction.

    UPDATE SIGNAL
    SET GreenTime = v_green_time,
        SignalStatus = 'GREEN'
    WHERE JunctionID = v_junction_id;


    DBMS_OUTPUT.PUT_LINE(
        'Camera ID          : ' || p_camera_id
    );

    DBMS_OUTPUT.PUT_LINE(
        'Vehicle Count      : ' || v_vehicle_count
    );

    DBMS_OUTPUT.PUT_LINE(
        'Traffic Density    : ' || v_density
    );

    DBMS_OUTPUT.PUT_LINE(
        'Recommended Green  : ' || v_green_time || ' seconds'
    );

    DBMS_OUTPUT.PUT_LINE(
        'Junction ID        : ' || v_junction_id
    );


EXCEPTION

    WHEN NO_DATA_FOUND THEN

        RAISE_APPLICATION_ERROR(
            -20003,
            'No vehicle-count data found for camera ' || p_camera_id
        );

    WHEN TOO_MANY_ROWS THEN

        RAISE_APPLICATION_ERROR(
            -20004,
            'Multiple junctions found for camera ' || p_camera_id
        );

END update_signal_timing;
/
SHOW ERRORS PROCEDURE update_signal_timing;


-- ============================================================
-- 4. PROCEDURE: CONGESTION REPORT
--
-- Displays the latest traffic condition for every camera.
-- ============================================================

CREATE OR REPLACE PROCEDURE congestion_report
IS

    v_found BOOLEAN := FALSE;

BEGIN

    DBMS_OUTPUT.PUT_LINE(
        '================================================'
    );

    DBMS_OUTPUT.PUT_LINE(
        '       TRAFFIC CONGESTION REPORT'
    );

    DBMS_OUTPUT.PUT_LINE(
        '================================================'
    );


    FOR rec IN (

        SELECT
            c.CameraID,
            j.JunctionName,
            r.RoadName,
            vc.VehicleCount,
            vc.Density,
            vc.Timestamp

        FROM CAMERA c

        JOIN ROAD r
            ON c.RoadID = r.RoadID

        JOIN JUNCTION j
            ON r.JunctionID = j.JunctionID

        JOIN (
            SELECT
                CameraID,
                VehicleCount,
                Density,
                Timestamp,
                CountID,
                ROW_NUMBER() OVER (
                    PARTITION BY CameraID
                    ORDER BY Timestamp DESC, CountID DESC
                ) AS rn
            FROM VEHICLECOUNT
        ) vc
            ON c.CameraID = vc.CameraID
           AND vc.rn = 1

        ORDER BY c.CameraID

    )
    LOOP

        v_found := TRUE;

        DBMS_OUTPUT.PUT_LINE(
            'Camera       : ' || rec.CameraID
        );

        DBMS_OUTPUT.PUT_LINE(
            'Junction     : ' || rec.JunctionName
        );

        DBMS_OUTPUT.PUT_LINE(
            'Road         : ' || rec.RoadName
        );

        DBMS_OUTPUT.PUT_LINE(
            'Vehicles     : ' || rec.VehicleCount
        );

        DBMS_OUTPUT.PUT_LINE(
            'Density      : ' || rec.Density
        );

        DBMS_OUTPUT.PUT_LINE(
            'Timestamp    : ' || rec.Timestamp
        );

        DBMS_OUTPUT.PUT_LINE(
            '------------------------------------------------'
        );

    END LOOP;


    IF NOT v_found THEN

        DBMS_OUTPUT.PUT_LINE(
            'No traffic data available.'
        );

    END IF;


END congestion_report;
/
SHOW ERRORS PROCEDURE congestion_report;


-- ============================================================
-- 5. PROCEDURE: EMERGENCY PRIORITY
--
-- Emergency priority is implemented as functionality.
-- No EmergencyVehicle entity/table is created.
--
-- When emergency priority is activated for a junction:
--   - Its signal becomes GREEN.
--   - Green time is temporarily set to 90 seconds.
-- ============================================================

CREATE OR REPLACE PROCEDURE emergency_priority (
    p_junction_id IN VARCHAR2
)
IS

    v_junction_name JUNCTION.JunctionName%TYPE;

BEGIN

    -- Verify that the junction exists.

    SELECT JunctionName
    INTO v_junction_name
    FROM JUNCTION
    WHERE JunctionID = p_junction_id;


    -- Give the junction priority.

    UPDATE SIGNAL
    SET SignalStatus = 'GREEN',
        GreenTime = 90
    WHERE JunctionID = p_junction_id;


    IF SQL%ROWCOUNT = 0 THEN

        RAISE_APPLICATION_ERROR(
            -20005,
            'No signal found for junction ' || p_junction_id
        );

    END IF;


    DBMS_OUTPUT.PUT_LINE(
        '================================================'
    );

    DBMS_OUTPUT.PUT_LINE(
        '         EMERGENCY PRIORITY ACTIVATED'
    );

    DBMS_OUTPUT.PUT_LINE(
        '================================================'
    );

    DBMS_OUTPUT.PUT_LINE(
        'Junction ID   : ' || p_junction_id
    );

    DBMS_OUTPUT.PUT_LINE(
        'Junction Name : ' || v_junction_name
    );

    DBMS_OUTPUT.PUT_LINE(
        'Signal Status : GREEN'
    );

    DBMS_OUTPUT.PUT_LINE(
        'Green Time    : 90 seconds'
    );

    DBMS_OUTPUT.PUT_LINE(
        '================================================'
    );


EXCEPTION

    WHEN NO_DATA_FOUND THEN

        RAISE_APPLICATION_ERROR(
            -20006,
            'Junction ' || p_junction_id || ' does not exist'
        );

END emergency_priority;
/
SHOW ERRORS PROCEDURE emergency_priority;


-- ============================================================
-- END OF PL/SQL DEFINITIONS
-- ============================================================