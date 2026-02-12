from config import Config

# This is a placeholder for actual database models
# For the MVP, we are using the in-memory state in room_manager
# But this prepares the project for SQLite/PostgreSQL later.

def init_db():
    print(f"Connecting to database at {Config.DATABASE_URL}...")
    # SQL Alchemy / Peewee / Prisma init logic goes here
