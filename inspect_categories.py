
import sqlite3

def inspect():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    all_tables = [row[0] for row in cursor.fetchall()]
    print(f"All tables: {all_tables}")
    tables = [t for t in ['men_categories', 'women_categories', 'kids_categories', 'categories', 'subcategories', 'fashion_categories'] if t in all_tables]
    for table in tables:
        print(f"\nContent of {table}:")
        try:
            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
        except Exception as e:
            print(f"Error reading {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect()
