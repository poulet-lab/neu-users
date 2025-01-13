from ast import literal_eval
from typing import Self

from aredis_om import Field, JsonModel, get_redis_connection
from neu_sdk.config import REDIS_URL
from neu_sdk.security import encrypt_password, password_strength
from pydantic import BaseModel, EmailStr, field_validator, model_validator


class UserBase(BaseModel):
    first_name: str = Field(index=True, full_text_search=True, max_length=32)
    last_name: str | None = Field(None, index=True, full_text_search=True, max_length=32)
    username: str = Field(index=True, full_text_search=True, max_length=16)
    email: EmailStr = Field(index=True, full_text_search=True, max_length=32)
    extra: dict | None = Field(None)


class User(JsonModel, UserBase):
    class Meta:
        database = get_redis_connection(url=REDIS_URL, decode_responses=True)

    password: str = Field()

    superuser: bool = Field(False, index=True)
    extra: str | None = Field(None, index=True, full_text_search=True)

    @field_validator("extra", mode="before")
    @classmethod
    def serialize_extra(cls, extra: dict | None) -> str:
        if isinstance(extra, dict):
            return str(extra)
        return extra


class UserCreate(UserBase):
    password: str = Field()
    repeat_password: str

    @model_validator(mode="after")
    def check_passwords(self) -> Self:
        if self.password != self.repeat_password:
            msg = "Passwords do not match"
            raise ValueError(msg)

        if password_strength(self.password):
            self.password = encrypt_password(self.password)

        return self


class UserPublic(UserBase):
    pk: str
    # TODO fix leak
    password: str = Field()

    @field_validator("extra", mode="before")
    @classmethod
    def deserialize_extra(cls, extra: str | None) -> dict:
        if isinstance(extra, str):
            return literal_eval(extra)
        return extra


class UserPublicRestricted(BaseModel):
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
            msg = "New passwords do not match"
            raise ValueError(msg)

        if self.password == self.old_password:
            msg = "New password cannot be the same as old one"
            raise ValueError(msg)

        if password_strength(self.password):
            self.password = encrypt_password(self.password)
