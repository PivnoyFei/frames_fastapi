import datetime
from typing import Optional

import ormar

from db import MainMata
from users.models import User


class Image(ormar.Model):
    class Meta(MainMata):
        pass

    id: int = ormar.Integer(primary_key=True)
    timestamp = ormar.DateTime(default=datetime.datetime.now)
    title: str = ormar.String(max_length=100)
    user: Optional[User] = ormar.ForeignKey(User, related_name="user")
