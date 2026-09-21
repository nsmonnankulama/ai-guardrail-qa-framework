import os
import sys
from urllib.parse import urlparse

import psycopg2
from psycopg2 import sql

from app.config import DATABASE_URL

ADMIN_URL = os.getenv("DB_BOOTSTRAP_ADMIN_URL", "")


def _wait_for_server(dsn: str, attempts: int = 10, delay: float = 2.0):
    import time

    last_exc = None
    for _ in range(attempts):
        try:
            conn = psycopg2.connect(dsn)
            conn.close()
            return
        except psycopg2.OperationalError as exc:
            last_exc = exc
            time.sleep(delay)
    raise last_exc


def bootstrap():
    if not DATABASE_URL.startswith("postgresql"):
        print("[db_bootstrap] DATABASE_URL is not postgres, nothing to provision.")
        return

    if not ADMIN_URL:
        print("[db_bootstrap] DB_BOOTSTRAP_ADMIN_URL not set, assuming database/role already exist.")
        return

    target = urlparse(DATABASE_URL)
    db_name = target.path.lstrip("/")
    db_user = target.username
    db_password = target.password

    admin_parsed = urlparse(ADMIN_URL)
    maintenance_dsn = (
        f"postgresql://{admin_parsed.username}:{admin_parsed.password}"
        f"@{admin_parsed.hostname}:{admin_parsed.port or 5432}/postgres"
    )

    print(f"[db_bootstrap] Checking role '{db_user}' and database '{db_name}' on {admin_parsed.hostname}...")
    _wait_for_server(maintenance_dsn)

    conn = psycopg2.connect(maintenance_dsn)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (db_user,))
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE ROLE {} WITH LOGIN PASSWORD %s").format(sql.Identifier(db_user)),
                    (db_password,),
                )
                print(f"[db_bootstrap] Created role '{db_user}'.")
            else:
                print(f"[db_bootstrap] Role '{db_user}' already exists.")

            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if cur.fetchone() is None:
                cur.execute(
                    sql.SQL("CREATE DATABASE {} OWNER {}").format(
                        sql.Identifier(db_name), sql.Identifier(db_user)
                    )
                )
                print(f"[db_bootstrap] Created database '{db_name}' owned by '{db_user}'.")
            else:
                print(f"[db_bootstrap] Database '{db_name}' already exists.")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        bootstrap()
    except Exception as exc:
        print(f"[db_bootstrap] FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
