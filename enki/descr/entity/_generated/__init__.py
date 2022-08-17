"""Generated base classes of entities of the file entities.xml"""

from .description import DESC_BY_UID
from .Account import AccountBase
from .Avatar import AvatarBase
from .Test import TestBase
from .TestNoBase import TestNoBaseBase
from .Monster import MonsterBase
from .NPC import NPCBase
from .Gate import GateBase

__all__ = [
    'DESC_BY_UID',
    'AccountBase',
    'AvatarBase',
    'TestBase',
    'TestNoBaseBase',
    'MonsterBase',
    'NPCBase',
    'GateBase'
]
