"""Seed the hermetic DuckDB fixture used by the self-test workflow.

Creates <project>/data/warehouse.duckdb with a small `users` table so the
self-test needs no network and no secrets. Run from anywhere:

    python test/fixtures/duckdb_project/seed.py
"""

from pathlib import Path

import duckdb

project = Path(__file__).resolve().parent
db_path = project / "data" / "warehouse.duckdb"
db_path.parent.mkdir(parents=True, exist_ok=True)

conn = duckdb.connect(str(db_path))
conn.execute("DROP TABLE IF EXISTS users")
conn.execute(
    """
    CREATE TABLE users AS
        SELECT 1 AS id, 'Alice' AS name, 'alice@example.com' AS email
        UNION ALL SELECT 2, 'Bob', 'bob@example.com'
        UNION ALL SELECT 3, 'John', 'john@example.com'
    """
)
count = conn.execute("SELECT count(*) FROM users").fetchone()[0]
conn.close()
print(f"seeded {count} rows into {db_path}")
