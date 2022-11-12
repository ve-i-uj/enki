"""Generated serializers for RPC of the entities."""

from .Account import AccountRPCSerializer
from .Avatar import AvatarRPCSerializer
from .components.Test import TestComponentRPCSerializer
from .components.TestNoBase import TestNoBaseComponentRPCSerializer
from .Monster import MonsterRPCSerializer
from .NPC import NPCRPCSerializer
from .Gate import GateRPCSerializer


SERIAZER_BY_ETYPE_UID = {
    AccountRPCSerializer.ENTITY_CLS_ID: AccountRPCSerializer,
    AvatarRPCSerializer.ENTITY_CLS_ID: AvatarRPCSerializer,
    TestComponentRPCSerializer.ENTITY_CLS_ID: TestComponentRPCSerializer,
    TestNoBaseComponentRPCSerializer.ENTITY_CLS_ID: TestNoBaseComponentRPCSerializer,
    MonsterRPCSerializer.ENTITY_CLS_ID: MonsterRPCSerializer,
    NPCRPCSerializer.ENTITY_CLS_ID: NPCRPCSerializer,
    GateRPCSerializer.ENTITY_CLS_ID: GateRPCSerializer,
    }

__all__ = [
    'SERIAZER_BY_ETYPE_UID',
    'AccountRPCSerializer',
    'AvatarRPCSerializer',
    'TestComponentRPCSerializer',
    'TestNoBaseComponentRPCSerializer',
    'MonsterRPCSerializer',
    'NPCRPCSerializer',
    'GateRPCSerializer',
    ]
