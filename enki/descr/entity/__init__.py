from typing import Dict

# TODO: [02.07.2021 burov_alexey@mail.ru]:
# 1) Документация
# 2) Скорей всего нужно наружу выдавать всё содержание _entity
from enki import dcdescr

from ._generated import *

DESC_BY_NAME: Dict[str, dcdescr.EntityDesc] = {}
try:
    DESC_BY_NAME.update({d.name: d for d in DESC_BY_UID.values()})
except NameError:
    pass

__all__ = ['DESC_BY_UID', 'DESC_BY_NAME']