
import sqlite3

def delete_accessories():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    try:
        # 1. Delete products with 'Accessories' in name
        cursor.execute("DELETE FROM store_product WHERE product_name LIKE '%Accessories%'")
        deleted_count = cursor.rowcount
        print(f"Deleted {deleted_count} products by name.")
        
        # 2. Check for categories or subcategories (though tables weren't found in the previous list)
        # We will skip those for now since they didn't appear in the table list.
        
        conn.commit()
        print("Database update successful.")
    except Exception as e:
        print(f"Error during deletion: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    delete_accessories()
