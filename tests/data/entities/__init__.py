from typing import Type

from enki.apps.clientapp.gameentity import ClientGameEntity

from .account import Account
from .avatar import Avatar
from .gate import Gate
from .monster import Monster
from .npc import NPC

ENTITY_CLS_BY_NAME: dict[str, type[ClientGameEntity]] = {
    "Account": Account,
    "Avatar": Avatar,
    "Monster": Monster,
    "Gate": Gate,
    "NPC": NPC,
}
