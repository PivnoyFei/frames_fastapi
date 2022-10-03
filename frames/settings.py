import os

DATABASE_URL = "sqlite:///sqlite.db"
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates/")
STATIC_ROOT = os.path.join(os.path.dirname(__file__), "static/")
TEST_ROOT = os.path.join(os.path.dirname(__file__), "tests/")
