from typing import Type

from enki.app.clientapp.gameentity import GameEntity

from .account import Account
from .avatar import Avatar
from .monster import Monster
from .gate import Gate
from .npc import NPC

ENTITY_CLS_BY_NAME: dict[str, Type[GameEntity]] = {
    'Account': Account,
    'Avatar': Avatar,
    'Monster': Monster,
    'Gate': Gate,
    'NPC': NPC,
}
