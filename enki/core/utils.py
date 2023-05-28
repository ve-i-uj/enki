from typing import overload

from .kbeenum import ComponentType
from .message import MessageSerializer, MsgDescr
from . import msgspec

_SERIALIZERS = {
    ComponentType.DBMGR: MessageSerializer(msgspec.app.dbmgr.SPEC_BY_ID),
    ComponentType.CELLAPPMGR: MessageSerializer(msgspec.app.cellappmgr.SPEC_BY_ID),
    ComponentType.CLIENT: MessageSerializer(msgspec.app.client.SPEC_BY_ID),
    ComponentType.MACHINE: MessageSerializer(msgspec.app.machine.SPEC_BY_ID),
    ComponentType.LOGGER: MessageSerializer(msgspec.app.logger.SPEC_BY_ID),
    ComponentType.INTERFACES: MessageSerializer(msgspec.app.interfaces.SPEC_BY_ID),
}


def get_serializer_for(comp_type):
    return _SERIALIZERS[comp_type]
