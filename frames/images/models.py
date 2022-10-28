from databases import Database
from sqlalchemy import Column, ForeignKey, Integer, String, Table, select

from db import metadata

inbox = Table(
    "inbox", metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", String),
    Column("title", String(100), unique=True),
    Column("user", ForeignKey("users.id")),
)


class Inbox:
    def __init__(self, database: Database):
        self.database = database

    async def get_image(self, pk: int):
        query = select([inbox]).where(inbox.c.id == pk)
        query = await self.database.fetch_one(query)
        return dict(query) if query else None

    async def get_image_user_title(self, pk: int):
        query = select(inbox.c.user, inbox.c.title).where(inbox.c.id == pk)
        query = await self.database.fetch_one(query)
        return dict(query) if query else None

    async def create_image(self, user: int, title: str, timestamp: str):
        query = inbox.insert().values(
            user=user, title=title, timestamp=timestamp)
        await self.database.execute(query)

    async def delete_image(self, pk: int):
        query = inbox.delete().where(inbox.c.id == pk)
        await self.database.execute(query)
