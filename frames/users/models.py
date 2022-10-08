import datetime

import ormar

from db import MainMata


class User(ormar.Model):
    class Meta(MainMata):
        pass

    id: int = ormar.Integer(primary_key=True)
    email: str = ormar.String(max_length=255, unique=True, nullable=False)
    password: str = ormar.String(max_length=255)
    username: str = ormar.String(max_length=25, unique=True)
    first_name: str = ormar.String(max_length=50)
    last_name: str = ormar.String(max_length=50)
    timestamp = ormar.DateTime(default=datetime.datetime.now)
