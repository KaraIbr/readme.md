import sqlite3

conn = sqlite3.connect("ventura.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]

for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
    count = cursor.fetchone()[0]
    if count > 0:
        print(f"{table}: {count} rows")
        cursor.execute(f'SELECT * FROM "{table}" LIMIT 3')
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()
        for r in rows:
            print(f"  {dict(zip(cols, r))}")
conn.close()
