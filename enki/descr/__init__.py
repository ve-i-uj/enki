"""Packet gives specification classes of server communication."""

from . import app, servererror, entity

# TODO: [12.07.2021 burov_alexey@mail.ru]:
# Нужно вычищать сгенерированный код полностью или учитывать, что код может
# быть недогенерирован до конца. Здесь падает на  TYPE_SPEC_BY_ID
try:
    from .deftype import TYPE_SPEC_BY_ID
except ImportError:
    pass
