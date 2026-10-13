from app.database.oracle import oracle_conn


def test_oracle_connection():
    query = """
        SELECT
            USER AS username,
            SYS_CONTEXT(
                'USERENV',
                'SERVICE_NAME'
            ) AS service_name
        FROM dual
    """

    result = oracle_conn.fetch_all(query)

    print("Oracle connection successful!")
    print(result)


if __name__ == "__main__":
    test_oracle_connection()
