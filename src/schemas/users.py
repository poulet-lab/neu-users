from pydantic import BaseModel, EmailStr, field_validator, model_validator
from aredis_om import JsonModel, Field, get_redis_connection

from neu_sdk.security import password_strength, encrypt_password
from neu_sdk.config import REDIS_URL


class UserBase(BaseModel):
    first_name: str = Field(index=True, full_text_search=True, max_length=32)
    last_name: str | None = Field(
        None, index=True, full_text_search=True, max_length=32
    )
    username: str = Field(index=True, full_text_search=True, max_length=16)
    password: str = Field()
    email: EmailStr = Field(index=True, full_text_search=True, max_length=32)
    extra: dict | None = Field(None)


class User(JsonModel, UserBase):
    class Meta:
        database = get_redis_connection(url=REDIS_URL, decode_responses=True)

    superuser: bool = Field(False, index=True)
    extra: str | None = Field(None, index=True, full_text_search=True)

    @field_validator("extra", mode="before")
    def serialize_extra(cls, extra: dict | None) -> str:
        if isinstance(extra, dict):
            return str(extra)
        return extra


class UserCreate(UserBase):
    @field_validator("password")
    def hash_password(cls, password: str) -> str:
        if password_strength(password):
            return encrypt_password(password)
        return password


class UserPublic(UserBase):
    pk: str

    @field_validator("extra", mode="before")
    def deserialize_extra(cls, extra: str | None) -> dict:
        if isinstance(extra, str):
            return eval(extra)
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
            raise ValueError("New passwords do not match")

        if self.password == self.old_password:
            raise ValueError("new password cannot be the same as old one")

        if password_strength(self.password):
            self.password = encrypt_password(self.password)
