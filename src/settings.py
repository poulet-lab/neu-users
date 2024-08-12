from typing import Literal
from dotenv import find_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Admin(BaseModel):
    first_name: str = "Admin"
    last_name: str = ""
    username: str = "admin"
    password: str = Field("Neu&1234")
    email: str = Field("neu@test.com")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="neu_",
        env_nested_delimiter="_",
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = Field("user")
    root_path: str = Field("/user")
    docs_url: str = Field("/docs")
    redis_url: str = Field("redis://localhost:6379/0")

    admin: Admin = Field(Admin())

    log_level: Literal[
        "critical",
        "error",
        "warning",
        "info",
        "debug",
    ] = Field("warning")


settings = Settings()
