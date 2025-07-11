"""Messages of the CellApp component.

These messages are predefined by the plugin (not generated).
"""

from enki.kbetype import FLOAT, INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    ENTITY_ID,
    GAME_TIME,
    UINT8_ARRAY,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

onRemoteMethodCall = MsgDescr(  # noqa: N816
    id=302,
    lenght=-1,
    name="Entity::onRemoteMethodCall",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onLoseWitness = MsgDescr(  # noqa: N816
    id=44,
    lenght=-1,
    name="Entity::onLoseWitness",
    args_type=FIXED,
    args=(ENTITY_ID,),
    desc="",
)

onGetWitnessFromBase = MsgDescr(  # noqa: N816
    id=43,
    lenght=-1,
    name="Entity::onGetWitnessFromBase",
    args_type=FIXED,
    args=(ENTITY_ID,),
    desc="",
)

setPosition_XYZ_float = MsgDescr(  # noqa: N816
    id=42,
    lenght=14,
    name="Entity::setPosition_XYZ_float",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        FLOAT,
        FLOAT,
        FLOAT,
    ),
    desc="",
)

setPosition_XZ_float = MsgDescr(  # noqa: N816
    id=41,
    lenght=12,
    name="Entity::setPosition_XZ_float",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        FLOAT,
        FLOAT,
    ),
    desc="",
)

setPosition_XYZ_int = MsgDescr(  # noqa: N816
    id=40,
    lenght=-1,
    name="Entity::setPosition_XYZ_int",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        INT32,
        INT32,
        INT32,
    ),
    desc="",
)

setPosition_XZ_int = MsgDescr(  # noqa: N816
    id=39,
    lenght=-1,
    name="Entity::setPosition_XZ_int",
    args_type=FIXED,
    args=(
        ENTITY_ID,
        INT32,
        INT32,
    ),
    desc="",
)

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="Cellapp::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onDbmgrInitCompleted = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Cellapp::onDbmgrInitCompleted",
    args_type=VARIABLE,
    args=(
        GAME_TIME,  # gametime
        ENTITY_ID,  # startID
        ENTITY_ID,  # endID
        COMPONENT_ORDER,  # startGlobalOrder
        COMPONENT_ORDER,  # startGroupOrder
        STRING,  # digest
    ),
    desc="An app requests to obtain a callback for an entityID segment (???)",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55101,
    lenght=12,
    name="Cellapp::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

onBroadcastCellAppDataChanged = MsgDescr(  # noqa: N816
    id=15,
    lenght=12,
    name="Cellapp::onBroadcastCellAppDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateCellEntityInNewSpaceFromBaseapp = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="Cellapp::onCreateCellEntityInNewSpaceFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onGetEntityAppFromDbmgr = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="Cellapp::onGetEntityAppFromDbmgr",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        STRING,  # username
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_ORDER,  # globalorderID
        COMPONENT_ORDER,  # grouporderID
        UINT32,  # intaddr
        UINT16,  # intport
        UINT32,  # extaddr
        UINT16,  # extport
        STRING,  # extaddrEx
    ),
    desc="",
)

onBroadcastGlobalDataChanged = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Cellapp::onBroadcastGlobalDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onCreateCellEntityFromBaseapp = MsgDescr(  # noqa: N816
    id=19,
    lenght=-1,
    name="Cellapp::onCreateCellEntityFromBaseapp",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="Cellapp::onRegisterNewApp",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        STRING,  # username
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_ORDER,  # globalorderID
        COMPONENT_ORDER,  # grouporderID
        UINT32,  # intaddr
        UINT16,  # intport
        UINT32,  # extaddr
        UINT16,  # extport
        STRING,  # extaddrEx
    ),
    desc="???",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=29,
    lenght=-1,
    name="Cellapp::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

SPEC_BY_ID = {
    onRemoteMethodCall.id: onRemoteMethodCall,
    onLoseWitness.id: onLoseWitness,
    onGetWitnessFromBase.id: onGetWitnessFromBase,
    setPosition_XYZ_float.id: setPosition_XYZ_float,
    setPosition_XZ_float.id: setPosition_XZ_float,
    setPosition_XYZ_int.id: setPosition_XYZ_int,
    setPosition_XZ_int.id: setPosition_XZ_int,
    lookApp.id: lookApp,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastCellAppDataChanged.id: onBroadcastCellAppDataChanged,
    onCreateCellEntityInNewSpaceFromBaseapp.id: onCreateCellEntityInNewSpaceFromBaseapp,
    onGetEntityAppFromDbmgr.id: onGetEntityAppFromDbmgr,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    onCreateCellEntityFromBaseapp.id: onCreateCellEntityFromBaseapp,
    onRegisterNewApp.id: onRegisterNewApp,
    reqCloseServer.id: reqCloseServer,
}

__all__ = [
    "SPEC_BY_ID",
    "lookApp",
    "onAppActiveTick",
    "onBroadcastCellAppDataChanged",
    "onBroadcastGlobalDataChanged",
    "onCreateCellEntityFromBaseapp",
    "onCreateCellEntityInNewSpaceFromBaseapp",
    "onDbmgrInitCompleted",
    "onGetEntityAppFromDbmgr",
    "onGetWitnessFromBase",
    "onLoseWitness",
    "onRegisterNewApp",
    "onRemoteMethodCall",
    "reqCloseServer",
    "setPosition_XYZ_float",
    "setPosition_XYZ_int",
    "setPosition_XZ_float",
    "setPosition_XZ_int",
]
