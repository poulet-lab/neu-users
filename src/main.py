from sys import _getframe
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from aredis_om import Migrator

from .logging import LOGGER
from .settings import settings
from .routes import router
from .schema import *


async def lifespan(app):
    await Migrator().run()

    try:
        if not await User.find(User.superuser == True).first():
            LOGGER.info(
                f"neu.{settings.service_name}.{__name__}.{_getframe().f_code.co_name}: creating superuser"
            )
            user = UserCreate(
                first_name=settings.admin.first_name,
                last_name=settings.admin.last_name,
                username=settings.admin.username,
                password=settings.admin.password,
                email=settings.admin.email,
            )
            user = User(
                **user.model_dump(exclude_unset=True, exclude_none=True),
                superuser=True,
            )
            await user.save()
        else:
            LOGGER.info(
                f"neu.{settings.service_name}.{__name__}.{_getframe().f_code.co_name}: superuser exists"
            )
    except Exception as e:
        LOGGER.error(f"{_getframe().f_code.co_name}: {e}")
        raise RuntimeError("Internal Server Error")

    yield


app = FastAPI(
    title="Neu Users",
    root_path=settings.root_path,
    docs_url=settings.docs_url,
    redoc_url=None,
    version="0.1.0",
    license_info={
        "name": "GNU Affero General Public License v3.0 or later",
        "identifier": "AGPL-3.0-or-later",
        "url": "https://www.gnu.org/licenses/agpl-3.0.txt",
    },
    lifespan=lifespan,
)


@app.get("/ping")
def ping():
    return JSONResponse(
        {
            "service_name": settings.service_name,
            "timestamp": datetime.now().strftime("%m/%d/%y %H:%M:%S"),
        }
    )


app.include_router(router)
