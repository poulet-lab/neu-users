from aredis_om import NotFoundError
from neu_sdk.config import LOGGER
from neu_sdk.interface import create_app
from uvicorn import run

from neu_users import __version__ as app_version
from neu_users.config import settings
from neu_users.routes import router
from neu_users.schemas import User, UserCreate
from neu_users.schemas import __version__ as schema_version


async def create_superuser():
    try:
        await User.find(User.superuser == True).first()
        LOGGER.info("Superuser found")
    except NotFoundError as e:
        LOGGER.info("Superuser not found and it will be created.")
        user = UserCreate(
            first_name="Superuser",
            username="superuser",
            password=settings.superuser.password,
            email=settings.superuser.email,
        )
        user = User.model_validate(user)
        user.superuser = True
        await user.save()


app = create_app(
    service_name="neu-users",
    tags=["neu", "microservice", "users"],
    app_version=app_version,
    schema_version=schema_version,
    lifespan_before=[create_superuser()],
)
app.include_router(router)

if __name__ == "__main__":
    run("main:app", host=settings.neu.service.host, port=settings.neu.service.port)
