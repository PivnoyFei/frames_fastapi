from typing import Union

from databases import Database
from sqlalchemy import Column, DateTime, Integer, String, Table, select
from sqlalchemy.sql import func

from db import metadata
from users.schemas import UserCreate

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), unique=True),
    Column("password", String(255)),
    Column("username", String(25), unique=True, index=True),
    Column("first_name", String(50)),
    Column("last_name", String(50)),
    Column("timestamp", DateTime(timezone=True), default=func.now()),
)


class User:
    def __init__(self, database: Database):
        self.database = database

    async def get_user_by_email(self, email: str) -> Union[int, None]:
        query = select(users.c.email).where(users.c.email == email)
        return await self.database.fetch_one(query)

    async def get_user_by_username(self, username: str) -> Union[int, None]:
        query = select(users.c.username).where(users.c.username == username)
        return await self.database.fetch_one(query)

    async def get_user_password_by_username(self, username: str):
        query = select(users.c.username, users.c.password).where(
            users.c.username == username)
        query = await self.database.fetch_one(query)
        return dict(query) if query else None

    async def get_user_full(self, username: str):
        query = select([users]).where(users.c.username == username)
        query = await self.database.fetch_one(query)
        return dict(query) if query else None

    async def create_user(self, user: UserCreate):
        query = users.insert().values(
            email=user.email,
            password=user.password,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        await self.database.execute(query)

    async def update_user(
        self, first_name: str, last_name: str, email: str, id: int
    ):
        query = users.update().where(users.c.id == id).values(
            first_name=first_name, last_name=last_name, email=email)
        await self.database.execute(query)
