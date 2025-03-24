from app.database import migrate_from_sqlite

if __name__ == "__main__":
    success = migrate_from_sqlite()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed.")