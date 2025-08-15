from typing import Type

from enki.apps.clientapp.gameentity import GameEntity

from .account import Account
from .avatar import Avatar
from .gate import Gate
from .monster import Monster
from .npc import NPC

ENTITY_CLS_BY_NAME: dict[str, type[GameEntity]] = {
    "Account": Account,
    "Avatar": Avatar,
    "Monster": Monster,
    "Gate": Gate,
    "NPC": NPC,
}
