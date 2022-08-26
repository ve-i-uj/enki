# TODO: [2022-08-19 12:04 burov_alexey@mail.ru]:
# Безобразие, надо подумать, как быть с импортом. Папка же передаётся с сущносями.
# Типа игра с плагином ожидает, что это хоть модуль буде.
# Просто entities должен содержать реализации всех сущностей.

from .account import Account
from .avatar import Avatar
from .monster import Monster
from .gate import Gate
from .npc import NPC
from . import components
