"""
Database connection helper.

Credentials come from environment variables (DB_HOST, DB_USER, DB_PASSWORD,
DB_NAME) instead of being hardcoded in source, so the real password is never
committed to git. For local development we also load a `.env` file if one
exists in the project root -- a tiny hand-rolled loader is used instead of
adding the `python-dotenv` dependency, since the format we need is just
KEY=VALUE lines.

Copy .env.example to .env and fill in your real local credentials; .env is
git-ignored.
"""

import os
import mysql.connector
from mysql.connector import Error


def _load_dotenv_if_present():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, ".env")

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            # Don't override a variable the environment already set.
            os.environ.setdefault(key, value)


_load_dotenv_if_present()


class MissingDatabaseConfig(Exception):
    pass


def _get_config():
    host = os.environ.get("DB_HOST")
    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    database = os.environ.get("DB_NAME")

    missing = [name for name, value in (
        ("DB_HOST", host), ("DB_USER", user), ("DB_PASSWORD", password), ("DB_NAME", database)
    ) if not value]

    if missing:
        raise MissingDatabaseConfig(
            "Missing required database configuration: " + ", ".join(missing) + ". "
            "Copy .env.example to .env and fill in your local database credentials."
        )

    return dict(host=host, user=user, password=password, database=database)


def create_connection():
    try:
        config = _get_config()
    except MissingDatabaseConfig as e:
        print("Configuration error:", e)
        return None

    try:
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            return connection

    except Error as e:
        print("Error connecting to MySQL:", e)

    return None


if __name__ == "__main__":
    connection = create_connection()

    if connection:
        connection.close()
        print("MySQL connection closed.")
