"""
Fix IAM permission overrides for karina@venergy.com.

The CHECK constraint says effect IN ('GRANT', 'DENY') (uppercase enum names).
But SQLAlchemy stores the StrEnum *value*, which is lowercase 'grant'/'deny'.
So we need LOWERCASE in the DB for SQLAlchemy to read them back correctly.
"""

import sqlite3

conn = sqlite3.connect("ventura.db")
cur = conn.cursor()

# First, check current state
cur.execute("SELECT id, user_id, permission, effect FROM iam_user_permission_override")
print("Before fix:")
for row in cur.fetchall():
    print(f"  id={row[0]} user={row[1]} perm={row[2]} effect={row[3]}")

# Update to lowercase values (SQLAlchemy StrEnum stores lowercase values)
cur.execute("UPDATE iam_user_permission_override SET effect = 'grant' WHERE effect = 'GRANT'")
cur.execute("UPDATE iam_user_permission_override SET effect = 'deny' WHERE effect = 'DENY'")

cur.execute("SELECT id, user_id, permission, effect FROM iam_user_permission_override")
print("After fix:")
for row in cur.fetchall():
    print(f"  id={row[0]} user={row[1]} perm={row[2]} effect={row[3]}")

conn.commit()
conn.close()
print("Done")
