from pathlib import Path
import pickle
from typing import Any
from .kbeenum import ComponentType
from .message import MessageSerializer
from . import msgspec

_SERIALIZERS = {
    ComponentType.DBMGR: MessageSerializer(msgspec.app.dbmgr.SPEC_BY_ID),
    ComponentType.BASEAPPMGR: MessageSerializer(msgspec.app.baseappmgr.SPEC_BY_ID),
    ComponentType.CELLAPPMGR: MessageSerializer(msgspec.app.cellappmgr.SPEC_BY_ID),
    ComponentType.CLIENT: MessageSerializer(msgspec.app.client.SPEC_BY_ID),
    ComponentType.MACHINE: MessageSerializer(msgspec.app.machine.SPEC_BY_ID),
    ComponentType.LOGGER: MessageSerializer(msgspec.app.logger.SPEC_BY_ID),
    ComponentType.INTERFACES: MessageSerializer(msgspec.app.interfaces.SPEC_BY_ID),
    ComponentType.BASEAPP: MessageSerializer(msgspec.app.baseapp.SPEC_BY_ID),
    ComponentType.CELLAPP: MessageSerializer(msgspec.app.cellapp.SPEC_BY_ID),
    ComponentType.LOGINAPP: MessageSerializer(msgspec.app.loginapp.SPEC_BY_ID),
}


def get_serializer_for(comp_type: ComponentType):
    return _SERIALIZERS[comp_type]


def pickle_global_data_value(data: bytes) -> Any:
    """Десериализовать закодированные KBEngine pickle данные.

    Для десериализации нужен модуль _upf.
    """
    try:
        value = pickle.loads(data)
    except ModuleNotFoundError as err:
        if str(err) == "No module named '_upf'":
            import sys
            sys.path.append(str(Path(__file__).parent))
            value = pickle.loads(data)
            sys.path.pop()
        else:
            raise err

    return value
