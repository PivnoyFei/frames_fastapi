import datetime

import ormar
from db import MainMata


class User(ormar.Model):
    class Meta(MainMata):
        pass

    id: int = ormar.Integer(primary_key=True)


class Image(ormar.Model):
    class Meta(MainMata):
        pass

    id: int = ormar.Integer(primary_key=True)
    timestamp = ormar.DateTime(default=datetime.datetime.now)
    title: str = ormar.String(max_length=100)
    # user = ormar.ForeignKey(User)
