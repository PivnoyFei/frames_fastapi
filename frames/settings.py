import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB", default="postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", default="postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", default="localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", default="5432")

TESTING = os.getenv("TESTING")

if TESTING:
    POSTGRES_SERVER = "db-test"
DATABASE_URL = f"postgresql://{POSTGRES_USER}:"\
               f"{POSTGRES_PASSWORD}@"\
               f"{POSTGRES_SERVER}:"\
               f"{POSTGRES_PORT}/"\
               f"{POSTGRES_DB}"

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates/")
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "static/")
TEST_ROOT = os.path.join(os.path.dirname(__file__), "tests/")

PK, PK_16 = 1, 16
FILE = "tolstoy."
