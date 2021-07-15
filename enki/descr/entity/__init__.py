from typing import Dict

# TODO: [02.07.2021 burov_alexey@mail.ru]:
# 1) Документация
# 2) Скорей всего нужно наружу выдавать всё содержание _entity
from ._generated import *
from ._entity import Entity, EntityDesc

DESC_BY_NAME: Dict[str, EntityDesc] = {}
try:
    DESC_BY_NAME.update({d.name: d for d in DESC_BY_UID.values()})
except NameError:
    pass

__all__ = ['DESC_BY_UID', 'DESC_BY_NAME']
