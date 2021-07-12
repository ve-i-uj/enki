# TODO: [02.07.2021 burov_alexey@mail.ru]:
# 1) Документация
# 2) Скорей всего нужно наружу выдавать всё содержание _entity
from ._generated import *
from ._entity import Entity, EntityDesc

try:
    DESC_BY_NAME = {d.name: d for d in DESC_BY_UID.values()}
except NameError:
    DESC_BY_NAME = {}

__all__ = ['DESC_BY_UID', 'DESC_BY_NAME']
