from odmantic import Model, Field


class User(Model):
    email: str = Field(index=True, unique=True)
    password: str
    admin: bool = Field(default=False)
