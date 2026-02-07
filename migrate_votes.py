"""
Migration script to add votes table to the database
Run this script to create the votes table for the feedback voting system
"""

from app import app, db, Vote
import sys

def migrate_votes_table():
    """Create the votes table in the database"""
    with app.app_context():
        try:
            # Create the votes table
            db.create_all()
            print("✓ Successfully created votes table")
            print("  - Table: vote")
            print("  - Columns: id, user_id, feedback_id, vote_type, created_at, updated_at")
            print("  - Constraints: unique(user_id, feedback_id), foreign keys with CASCADE delete")
            return True
        except Exception as e:
            print(f"✗ Error creating votes table: {e}")
            return False

if __name__ == '__main__':
    print("Starting database migration for feedback voting system...")
    print("-" * 60)
    
    success = migrate_votes_table()
    
    print("-" * 60)
    if success:
        print("Migration completed successfully!")
        sys.exit(0)
    else:
        print("Migration failed!")
        sys.exit(1)
