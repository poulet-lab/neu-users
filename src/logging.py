from logging import getLogger
from neu_sdk.config import setup_logging
from .settings import settings

LOGGER = getLogger(f"neu.{settings.service_name}")
setup_logging(logger=LOGGER, level=settings.log_level.upper())
