from re import match
from bcrypt import hashpw, gensalt
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from aredis_om import JsonModel, Field, get_redis_connection
from .settings import settings


def password_strength(password):
    if not match(
        r"^.*(?=.{8})(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@£$%^&*()_+={}?:~\[\]])[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$",
        password,
    ):
        raise ValueError(
            "Password must be at least 8 characters long and include at least one number, one lowercase letter, one uppercase letter, and one special character."
        )
    return True


class UserBase(BaseModel):
    first_name: str = Field(index=True, full_text_search=True, max_length=32)
    last_name: str | None = Field(
        None, index=True, full_text_search=True, max_length=32
    )
    username: str = Field(index=True, full_text_search=True, max_length=16)
    password: str = Field(index=True)
    email: EmailStr = Field(index=True, full_text_search=True, max_length=32)


class User(JsonModel, UserBase, extra="ignore"):
    class Meta:
        database = get_redis_connection(url=settings.redis_url, decode_responses=True)

    superuser: bool = Field(False, index=True)
    extra: str | None = Field(None, index=True, full_text_search=True)

    @field_validator("extra", mode="before")
    def serialize_extra(cls, extra: dict | None) -> str:
        if isinstance(extra, dict):
            return str(extra)
        return extra


class UserCreate(UserBase, extra="ignore"):
    extra: dict | None = Field(None)

    @field_validator("password")
    def hash_password(cls, password: str) -> str:
        if password_strength(password):
            return hashpw(password.encode(), gensalt()).decode()
        return password


class UserPublic(UserBase, extra="ignore"):
    extra: dict | None = Field(None)

    @field_validator("extra", mode="before")
    def deserialize_extra(cls, extra: str | None) -> dict:
        if isinstance(extra, str):
            return eval(extra)
        return extra


class UserPublicRestricted(BaseModel, extra="ignore"):
    pk: str
    username: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    extra: dict | None = None


class UserPasswordUpdate(BaseModel):
    old_password: str
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def check_passwords(self):
        if self.password != self.repeat_password:
            raise ValueError("New passwords do not match")

        if self.password == self.old_password:
            raise ValueError("new password cannot be the same as old one")

        if password_strength(self.password):
            self.password = hashpw(self.password.encode(), gensalt()).decode()
        return self
