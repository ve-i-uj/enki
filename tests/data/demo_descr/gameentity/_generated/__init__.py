"""Generated base classes of entities of the file entities.xml"""

from enki.app.gameentity import GameEntity

from .Account import AccountBase
from .Avatar import AvatarBase
from .components.Test import TestBase
from .components.TestNoBase import TestNoBaseBase
from .Monster import MonsterBase
from .NPC import NPCBase
from .Gate import GateBase


GAME_ENTITY_BY_TYPE_NAME: dict[str, GameEntity] = {
    'AccountBase': AccountBase,
    'AvatarBase': AvatarBase,
    'TestBase': TestBase,
    'TestNoBaseBase': TestNoBaseBase,
    'MonsterBase': MonsterBase,
    'NPCBase': NPCBase,
    'GateBase': GateBase,
}

__all__ = [
    'GAME_ENTITY_BY_TYPE_NAME',
    'AccountBase',
    'AvatarBase',
    'TestBase',
    'TestNoBaseBase',
    'MonsterBase',
    'NPCBase',
    'GateBase',
]
