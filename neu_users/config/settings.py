from dotenv import find_dotenv
from neu_sdk.config.settings import Settings as DefaultSettings
from pydantic import BaseModel, EmailStr, Field
from pydantic_settings import SettingsConfigDict


class Superuser(BaseModel):
    password: str = Field("Neu123@!")
    email: EmailStr = Field("info@neu.com")


class Settings(DefaultSettings):
    model_config = SettingsConfigDict(
        env_nested_delimiter="_",
        env_file=find_dotenv(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    superuser: Superuser = Superuser()


settings = Settings()
