from sqlalchemy.engine.url import make_url

from app.core.config import settings
import psycopg2

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
cur.execute(
    "SELECT pid, state FROM pg_stat_activity WHERE datname=%s AND pid <> pg_backend_pid()",
    (url.database,),
)
for pid, state in cur.fetchall():
    print(f"terminating {pid} {state}")
    cur.execute("SELECT pg_terminate_backend(%s)", (pid,))
print("done")
conn.close()
