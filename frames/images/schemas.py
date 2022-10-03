from datetime import date

from pydantic import BaseModel


class GetUser(BaseModel):
    id: str


class GetImage(BaseModel):
    id: int
    # user: GetUser
    title: str
    timestamp: date