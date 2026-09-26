from __future__ import annotations

import psycopg2
from sqlalchemy.engine.url import make_url

from app.core.config import settings


def main() -> None:
    url = make_url(settings.DATABASE_URL)
    conn = psycopg2.connect(
        host=url.host,
        port=url.port,
        user=url.username,
        password=url.password,
        dbname="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (url.database,))
    if cur.fetchone():
        print(f"database '{url.database}' already exists")
    else:
        cur.execute(f'CREATE DATABASE "{url.database}"')
        print(f"database '{url.database}' created")
    conn.close()


if __name__ == "__main__":
    main()
