from uvicorn import run
from neu_sdk.config import settings
from neu_sdk.interface import create_app

from routes import router
from schema import *

app = create_app(service_id="neu-users", tags=["neu", "microservice", "users"])
app.include_router(router)

if __name__ == "__main__":
    run("main:app", host=settings.service.host, port=settings.service.port)
