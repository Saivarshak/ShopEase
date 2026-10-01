import os
import psycopg2

conn = psycopg2.connect(os.environ['SOURCE_DB_URL'], connect_timeout=15, sslmode='require')
try:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cur.fetchall()]
        print('TABLES')
        for table in tables:
            print(table)
        print('COUNTS')
        for table in tables:
            cur.execute('SELECT COUNT(*) FROM ' + '"' + table.replace('"', '""') + '"')
            print(table, cur.fetchone()[0])
finally:
    conn.close()
