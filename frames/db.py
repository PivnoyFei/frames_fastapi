import databases
import ormar
import sqlalchemy

from settings import DATABASE_URL

metadata = sqlalchemy.MetaData()
database = databases.Database(DATABASE_URL)
engine = sqlalchemy.create_engine(DATABASE_URL)


class MainMata(ormar.ModelMeta):
    metadata = metadata
    database = database
