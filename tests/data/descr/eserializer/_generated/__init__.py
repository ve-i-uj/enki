"""Generated serializers for RPC of the entities."""

from typing import Type

from enki.apps.clientapp.eserializer import IEntityRPCSerializer

from .Account import AccountRPCSerializer
from .Avatar import AvatarRPCSerializer
from .components.Test import TestComponentRPCSerializer
from .components.TestNoBase import TestNoBaseComponentRPCSerializer
from .Gate import GateRPCSerializer
from .Monster import MonsterRPCSerializer
from .NPC import NPCRPCSerializer

SERIAZER_BY_ECLS_NAME: dict[str, type[IEntityRPCSerializer]] = {
    "Account": AccountRPCSerializer,
    "Avatar": AvatarRPCSerializer,
    "Monster": MonsterRPCSerializer,
    "NPC": NPCRPCSerializer,
    "Gate": GateRPCSerializer,
}

__all__ = [
    "SERIAZER_BY_ECLS_NAME",
    "AccountRPCSerializer",
    "AvatarRPCSerializer",
    "GateRPCSerializer",
    "MonsterRPCSerializer",
    "NPCRPCSerializer",
    "TestComponentRPCSerializer",
    "TestNoBaseComponentRPCSerializer",
]
