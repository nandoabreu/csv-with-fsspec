# -*- coding: utf-8 -*-
"""Project configuration file.

*** Update `env.toml` and run `make` to set `.env`. ***

This module manages environment variables and fallback values:
- Modify only to add/remove vars or to update fallback values.
- Use the Makefile to keep `.env` updated (values in `.env` are not persistent).

*** `.env` should be deployed to production. ***

Regarding decouple, the dependency responsible for fetching environment variables, the precedence order is:
- command-line variable > .env file > fallback value (if set)
"""
from decouple import config
from pathlib import Path
from tempfile import gettempdir

LOG_LEVEL: str = config('LOG_LEVEL', default='INFO')
ENABLE_STDOUT_LOG: bool = config('ENABLE_STDOUT_LOG', cast=bool, default=True)

APP_NAME: str = config('APP_NAME', default='App Name')
APP_VERSION: str = config('APP_VERSION', default='0.1.0')
PROJECT_NAME: str = config('PROJECT_NAME', default=APP_NAME).replace(' ', '-').lower()
PROJECT_DESCRIPTION: str = config('PROJECT_DESCRIPTION', default=APP_NAME)

LOG_ROTATION_MAX_MB: float = config('LOG_ROTATION_MAX_MB', cast=float, default='9')
LOG_MAX_ROTATED_FILES: int = config('LOG_MAX_ROTATED_FILES', cast=int, default='5')

LOGS_DIR: Path = Path(config('LOGS_DIR', default=f'/{gettempdir()}/{PROJECT_NAME}')).resolve()
APP_DIR: Path = Path(config('APP_DIR', default='app')).resolve()
SRC_BASE_DIR: Path = Path(__file__).resolve().parent.parent
PROJECT_ROOT_DIR: Path = SRC_BASE_DIR.parent

SOURCE_XML_URL: str = config('SOURCE_XML_URL')
DOWNLOAD_LINK_INDEX: int = config('DOWNLOAD_LINK_INDEX', cast=int, default=1)

STORAGE_LOCAL_DIR: str = config('STORAGE_LOCAL_DIR')
