from neu_sdk.config import settings
from neu_sdk.interface import create_app
from uvicorn import run

from neu_users import __version__ as app_version
from neu_users.routes import router
from neu_users.schemas import *
from neu_users.schemas import __version__ as schema_version

app = create_app(
    service_name="neu-users",
    tags=["neu", "microservice", "users"],
    app_version=app_version,
    schema_version=schema_version,
)
app.include_router(router)

if __name__ == "__main__":
    run("main:app", host=settings.neu.service.host, port=settings.neu.service.port)
