
from app.database.neo4j import neo4j_conn

def main():
    try:
        result = neo4j_conn.run_query(
            "RETURN 'Neo4j connection successful!' AS message"
        )
        print(result)
        print("Connection test passed!")

    except Exception as e:
        print("Connection test failed:")
        print(type(e).__name__, str(e))

    finally:
        neo4j_conn.close()

if __name__ == "__main__":
    main()

