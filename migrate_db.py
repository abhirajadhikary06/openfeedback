"""
Database Migration Script
Run this script to add authentication tables to your existing database
"""

import sqlite3
import os

def migrate_database():
    """Migrate existing database to add user authentication"""
    
    db_path = 'instance/openfeed.db'
    
    if not os.path.exists('instance'):
        os.makedirs('instance')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Step 1: Create users table
    print("Creating users table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')
    
    # Step 2: Check if old feedback table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
    old_table_exists = cursor.fetchone() is not None
    
    # Step 3: Create new feedback table with user_id
    print("Creating new feedback table...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Step 4: Migrate data from old table if it exists
    if old_table_exists:
        print("Migrating data from old feedback table...")
        
        # Get columns from old table
        cursor.execute("PRAGMA table_info(feedback)")
        old_columns = [column[1] for column in cursor.fetchall()]
        
        # Build insert query based on available columns
        select_parts = []
        insert_columns = ['user_id']
        
        for col in ['title', 'description', 'category', 'status', 'created_at']:
            if col in old_columns:
                select_parts.append(col)
                insert_columns.append(col)
        
        if select_parts:
            # Migrate existing data (user_id will be NULL for old entries)
            query = f'''
                INSERT INTO feedback_new ({', '.join(insert_columns)})
                SELECT NULL, {', '.join(select_parts)}
                FROM feedback
            '''
            cursor.execute(query)
            print(f"Migrated {cursor.rowcount} records from old feedback table")
        
        # Rename old table as backup
        cursor.execute('ALTER TABLE feedback RENAME TO feedback_old_backup')
        print("Old feedback table renamed to 'feedback_old_backup'")
    
    # Step 5: Create admin user (optional - comment out if not needed)
    print("Creating default admin user...")
    from werkzeug.security import generate_password_hash
    
    try:
        admin_password_hash = generate_password_hash('admin123')  # Change this password!
        cursor.execute(
            'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
            ('admin', 'admin@example.com', admin_password_hash, 1)
        )
        print("Admin user created (username: admin, password: admin123)")
        print("  IMPORTANT: Change the admin password after first login!")
    except sqlite3.IntegrityError:
        print("Admin user already exists, skipping...")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n Migration completed successfully!")
    print("\nNext steps:")
    print("1. Copy auth.py to your project root directory")
    print("2. Copy the HTML templates to your templates/ folder")
    print("3. Update your app.py with the authentication integration")
    print("4. Change the admin password!")

if __name__ == '__main__':
    migrate_database()