"""Packet gives specification classes of server communication."""

from . import app, servererror, entity
from .app import MessageDescr, MsgArgsType

# TODO: [12.07.2021 burov_alexey@mail.ru]:
# Нужно вычищать сгенерированный код полностью или учитывать, что код может
# быть недогенерирован до конца. Здесь падает на  TYPE_SPEC_BY_ID
try:
    from ._deftype import TYPE_SPEC_BY_ID, DataTypeDescr
except ImportError:
    pass
