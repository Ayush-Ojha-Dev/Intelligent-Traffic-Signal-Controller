// ============================================================
// seed.cypher
// Sample data for the Intelligent Traffic Signal Controller
// graph model. Run this in Neo4j Browser or via
// `cypher-shell -f seed.cypher` after starting a fresh database.
//
// Graph shape:
//   (:Junction)-[:HAS_ROAD]->(:Road)
//   (:Road)-[:HAS_CAMERA]->(:Camera)
//   (:Camera)-[:RECORDS]->(:VehicleCount)
//   (:Junction)-[:CONTROLS]->(:Signal)
// ============================================================

// Clear existing demo data (safe to skip on a brand-new DB).
MATCH (n) DETACH DELETE n;

// --- Junctions ---
CREATE (j1:Junction {junction_id: 'J01', junction_name: 'Anna Nagar Junction', location: 'Chennai'});
CREATE (j2:Junction {junction_id: 'J02', junction_name: 'Tambaram Junction',  location: 'Chennai'});

// --- Roads ---
MATCH (j1:Junction {junction_id: 'J01'})
CREATE (r1:Road {road_id: 'R01', road_name: '100 Feet Road', length: 3.2, speed_limit: 50})
CREATE (j1)-[:HAS_ROAD]->(r1);

MATCH (j2:Junction {junction_id: 'J02'})
CREATE (r2:Road {road_id: 'R02', road_name: 'GST Road', length: 5.0, speed_limit: 60})
CREATE (j2)-[:HAS_ROAD]->(r2);

// --- Cameras ---
MATCH (r1:Road {road_id: 'R01'})
CREATE (c1:Camera {camera_id: 'C01', location: 'Anna Nagar - North', status: 'ACTIVE'})
CREATE (r1)-[:HAS_CAMERA]->(c1);

MATCH (r2:Road {road_id: 'R02'})
CREATE (c2:Camera {camera_id: 'C02', location: 'Tambaram - East', status: 'ACTIVE'})
CREATE (r2)-[:HAS_CAMERA]->(c2);

// --- Signals ---
MATCH (j1:Junction {junction_id: 'J01'})
CREATE (s1:Signal {signal_id: 'S01', signal_status: 'RED', green_time: 20, red_time: 40})
CREATE (j1)-[:CONTROLS]->(s1);

MATCH (j2:Junction {junction_id: 'J02'})
CREATE (s2:Signal {signal_id: 'S02', signal_status: 'RED', green_time: 20, red_time: 40})
CREATE (j2)-[:CONTROLS]->(s2);

// --- Sample VehicleCount observations ---
MATCH (c1:Camera {camera_id: 'C01'})
CREATE (vc1:VehicleCount {count_id: 'VC01', vehicle_count: 25, density: 'LOW', timestamp: timestamp()})
CREATE (c1)-[:RECORDS]->(vc1);

MATCH (c2:Camera {camera_id: 'C02'})
CREATE (vc2:VehicleCount {count_id: 'VC02', vehicle_count: 72, density: 'HIGH', timestamp: timestamp()})
CREATE (c2)-[:RECORDS]->(vc2);
