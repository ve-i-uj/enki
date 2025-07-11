"""ClientApp messages."""

from enki.core.message import MsgDescr as _MsgDescr

from ._generated import *
from ._client import *

# TODO: [burov_alexey@mail.ru 01.07.2025 13:16]
# Такую переменную нужно заворачивать в объект. Сейчас здесь какая-то непонятная магия
SPEC_BY_ID: dict[int, _MsgDescr] = {}
SPEC_BY_ID.update(_generated.SPEC_BY_ID)
SPEC_BY_ID.update(_client.SPEC_BY_ID)
