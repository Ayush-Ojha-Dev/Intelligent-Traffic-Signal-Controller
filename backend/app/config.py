"""
config.py
---------
Central place for all configuration values.

Reads settings from environment variables (and a local .env file, if
present) using pydantic-settings. Every value has a sensible default so
that the application can start even before the .env file is filled in
with real Neo4j / Oracle credentials — this matters for the first
project review, where we mostly work with dummy data and don't want a
missing DB connection to crash the whole API.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---- Neo4j (graph database) ----
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # ---- Oracle (relational database / PL-SQL) ----
    ORACLE_USER: str = "system"
    ORACLE_PASSWORD: str = "oracle"
    ORACLE_DSN: str = "localhost:1521/XEPDB1"

    # ---- App ----
    APP_NAME: str = "Intelligent Traffic Signal Controller"
    ENV: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single shared settings instance, imported everywhere else.
settings = Settings()
