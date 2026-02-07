"""
Fix the vote table by adding the missing updated_at column
"""

import sqlite3

def fix_vote_table():
    """Add updated_at column to vote table"""
    conn = sqlite3.connect('instance/openfeed.db')
    cursor = conn.cursor()
    
    try:
        # Check if updated_at column exists
        cursor.execute("PRAGMA table_info(vote)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'updated_at' not in columns:
            print("Adding updated_at column to vote table...")
            cursor.execute("""
                ALTER TABLE vote 
                ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            """)
            conn.commit()
            print("✓ Successfully added updated_at column")
        else:
            print("✓ updated_at column already exists")
        
        # Verify the table structure
        cursor.execute("PRAGMA table_info(vote)")
        print("\nCurrent vote table structure:")
        for row in cursor.fetchall():
            print(f"  - {row[1]} ({row[2]})")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    fix_vote_table()
