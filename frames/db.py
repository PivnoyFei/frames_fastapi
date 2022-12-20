import databases
import sqlalchemy

from settings import DATABASE_SQLITE, DATABASE_URL, USE_POSTGRES

metadata = sqlalchemy.MetaData()


if not USE_POSTGRES:
    DATABASE_URL = DATABASE_SQLITE
    database = databases.Database(DATABASE_URL)
    engine = sqlalchemy.create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
    print("Connection to PostgreSQL DB successful.")
else:
    database = databases.Database(DATABASE_URL)
    engine = sqlalchemy.create_engine(DATABASE_URL)

TEST_DATABASE_URL = DATABASE_URL
