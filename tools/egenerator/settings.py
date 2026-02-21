"""Настройки скрипта для генерации кода сообщнений и RPC."""

import logging
from pathlib import Path

import environs
from marshmallow.validate import Length

# TODO: [2026-02-11 16:33 burov_alexey@mail.ru]:
# Всё это нужно на входе читать и выводить ошибки. Здесь только константы.
_env = environs.Env()


GAME_ACCOUNT_NAME: str = _env.str("GAME_ACCOUNT_NAME", validate=[Length(min=1)])
GAME_PASSWORD: str = _env.str("GAME_PASSWORD", validate=[Length(min=1)])

GAME_GENERATED_CLIENT_API_DIR: Path = _env.path("GAME_GENERATED_CLIENT_API_DIR")
assert Path() != GAME_GENERATED_CLIENT_API_DIR, (
    'The variable "GAME_GENERATED_CLIENT_API_DIR" cannot be empty'
)


class CodeGenDstPath:
    ROOT: Path = GAME_GENERATED_CLIENT_API_DIR
    APP: Path = ROOT / "app"
    SERIALIZER_ENTITY: Path = ROOT / "eserializer" / "_generated"
    ENTITY: Path = ROOT / "gameentity" / "_generated"
    TYPE: Path = ROOT / "deftype/_generated.py"
    SERVERERROR: Path = ROOT / "servererror/_generated.py"
    KBENGINE_XML: Path = ROOT / "kbenginexml.py"


# Include description of the kbengine messages in the generated code
INCLUDE_MSGES: bool = _env.bool("INCLUDE_MSGES", False)
# Коды ошибок от сервера. В enki используется захардкоженный enum, динамическое
# обновление ошибок не используется.
INCLUDE_ERRORS: bool = _env.bool("INCLUDE_MSGES", False)

LOG_LEVEL: int = _env.log_level("LOG_LEVEL", logging.DEBUG)

PROJECT_SITE: str = "https://github.com/ve-i-uj/enki"

# Директория расположения шаблонов для генерации кода
JINJA_TEMPLS_DIR: Path = Path(__file__).parent / "templates"
