import sqlite3
from pathlib import Path

def ensure_sqlite(sqlite_path: str):
    Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(sqlite_path)
    cur = con.cursor()
    # demo table
    cur.execute("""            CREATE TABLE IF NOT EXISTS dept_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university TEXT,
            department TEXT,
            year INTEGER,
            employment_rate REAL
        );
    """)
    con.commit()
    con.close()
