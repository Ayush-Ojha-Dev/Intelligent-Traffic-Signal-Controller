# Intelligent Traffic Signal Controller

A mini-project that dynamically adjusts traffic signal timing based on
vehicle flow, using Neo4j (graph DB) for the traffic network and
Oracle/PL-SQL for the relational/reporting component.

## Entities (fixed, per project spec)

`Road`, `Junction`, `Camera`, `VehicleCount`, `Signal` — no other
entities (e.g. no separate `EmergencyVehicle`). Emergency priority is
implemented as a **procedure/behaviour**, not an entity.

## Architecture

```
Camera / YOLO
      |
Vehicle Count
      |
FastAPI Backend
      |
 +-----------+
 |           |
Neo4j      Oracle
 |           |
Graph      PL/SQL
 |           |
 +-----+-----+
       |
   Dashboard
```

## Folder structure

```
traffic-signal-controller/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + router registration
│   │   ├── api/                 # One router per entity
│   │   ├── services/            # Business logic (density/timing, Neo4j queries)
│   │   ├── database/            # Neo4j + Oracle connection wrappers
│   │   ├── models/               # Pydantic schemas
│   │   └── config.py            # Settings (.env driven)
│   ├── requirements.txt
│   └── .env
├── database/
│   ├── oracle/
│   │   ├── tables.sql           # Relational schema (BCNF)
│   │   └── procedures.sql       # PL/SQL: density, timing, congestion, emergency
│   └── neo4j/
│       └── seed.cypher          # Sample graph data
├── detection/
│   └── vehicle_detection.py     # Placeholder for later YOLO integration
└── README.md
```

## Setup

1. **Install dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure `.env`** (already has working defaults; edit if your
   Neo4j/Oracle credentials differ):

   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=password
   ```

3. **(Optional for now) Start Neo4j** and load sample data:

   ```bash
   cypher-shell -u neo4j -p password -f database/neo4j/seed.cypher
   ```

   The API works even without Neo4j running — `POST /vehicle-counts`
   still returns density + signal timing; only the persistence step
   silently no-ops if the DB is unreachable. This is intentional, so
   you can demo the core logic before Neo4j is set up.

4. **Run the backend**

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

5. **Open the interactive docs**: http://127.0.0.1:8000/docs

## Quick test (no Neo4j required)

```bash
curl -X POST http://127.0.0.1:8000/vehicle-counts \
  -H "Content-Type: application/json" \
  -d '{"camera_id": "C01", "vehicle_count": 72}'
```

Expected response:

```json
{
  "camera_id": "C01",
  "vehicle_count": 72,
  "density": "HIGH",
  "recommended_green_time": 60
}
```

## First-review scope

This backend covers everything needed for the ~30% first-review
demo: entity APIs, the vehicle-count -> density -> signal-time
pipeline, the Neo4j graph model + seed data, and the Oracle/PL-SQL
schema + procedures. Raspberry Pi, IR sensors, real YOLO detection,
and the dashboard are intentionally deferred to later milestones.
