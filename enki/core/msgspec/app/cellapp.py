"""Messages of the CellApp component.

These messages are predefined by the plugin (not generated).
"""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


onRemoteMethodCall = MsgDescr(
    id=302,
    lenght=-1,
    name='Entity::onRemoteMethodCall',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(kbetype.UINT8_ARRAY, ),
    desc=''
)

onLoseWitness = MsgDescr(
    id=44,
    lenght=-1,
    name='Entity::onLoseWitness',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
    ),
    desc=''
)

onGetWitnessFromBase = MsgDescr(
    id=43,
    lenght=-1,
    name='Entity::onGetWitnessFromBase',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
    ),
    desc=''
)

setPosition_XYZ_float = MsgDescr(
    id=42,
    lenght=14,
    name='Entity::setPosition_XYZ_float',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

setPosition_XZ_float = MsgDescr(
    id=41,
    lenght=12,
    name='Entity::setPosition_XZ_float',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.FLOAT,
        kbetype.FLOAT,
    ),
    desc=''
)

setPosition_XYZ_int = MsgDescr(
    id=40,
    lenght=-1,
    name='Entity::setPosition_XYZ_int',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.INT32,
        kbetype.INT32,
        kbetype.INT32,
    ),
    desc=''
)

setPosition_XZ_int = MsgDescr(
    id=39,
    lenght=-1,
    name='Entity::setPosition_XZ_int',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.INT32,
        kbetype.INT32,
    ),
    desc=''
)

lookApp = MsgDescr(
    id=9,
    lenght=-1,
    name='Cellapp::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

onDbmgrInitCompleted = MsgDescr(
    id=13,
    lenght=-1,
    name='Cellapp::onDbmgrInitCompleted',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.GAME_TIME,  # gametime
        kbetype.ENTITY_ID,  # startID
        kbetype.ENTITY_ID,  # endID
        kbetype.COMPONENT_ORDER,  # startGlobalOrder
        kbetype.COMPONENT_ORDER,  # startGroupOrder
        kbetype.STRING,  # digest
    ]),
    desc='An app requests to obtain a callback for an entityID segment (???)'
)

onAppActiveTick = MsgDescr(
    id=55101,
    lenght=12,
    name='Cellapp::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

onBroadcastCellAppDataChanged = MsgDescr(
    id=15,
    lenght=12,
    name='Cellapp::onBroadcastCellAppDataChanged',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

onCreateCellEntityInNewSpaceFromBaseapp = MsgDescr(
    id=16,
    lenght=-1,
    name='Cellapp::onCreateCellEntityInNewSpaceFromBaseapp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

onGetEntityAppFromDbmgr = MsgDescr(
    id=11,
    lenght=-1,
    name='Cellapp::onGetEntityAppFromDbmgr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.INT32,  # uid
        kbetype.STRING,  # username
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.COMPONENT_ORDER,  # globalorderID
        kbetype.COMPONENT_ORDER,  # grouporderID
        kbetype.UINT32,  # intaddr
        kbetype.UINT16,  # intport
        kbetype.UINT32,  # extaddr
        kbetype.UINT16,  # extport
        kbetype.STRING,  # extaddrEx
    ]),
    desc=''
)

onBroadcastGlobalDataChanged = MsgDescr(
    id=14,
    lenght=-1,
    name='Cellapp::onBroadcastGlobalDataChanged',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

onCreateCellEntityFromBaseapp = MsgDescr(
    id=19,
    lenght=-1,
    name='Cellapp::onCreateCellEntityFromBaseapp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name='Cellapp::onRegisterNewApp',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.INT32,  # uid
        kbetype.STRING,  # username
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.COMPONENT_ORDER,  # globalorderID
        kbetype.COMPONENT_ORDER,  # grouporderID
        kbetype.UINT32,  # intaddr
        kbetype.UINT16,  # intport
        kbetype.UINT32,  # extaddr
        kbetype.UINT16,  # extport
        kbetype.STRING,  # extaddrEx
    ]),
    desc='???'
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
}

__all__ = [
    'SPEC_BY_ID',
    'onRemoteMethodCall',
    'onLoseWitness',
    'onGetWitnessFromBase',
    'setPosition_XYZ_float',
    'setPosition_XZ_float',
    'setPosition_XYZ_int',
    'setPosition_XZ_int',

    'lookApp',
    'onDbmgrInitCompleted',
    'onAppActiveTick',
    'onBroadcastCellAppDataChanged',
    'onCreateCellEntityInNewSpaceFromBaseapp',
    'onGetEntityAppFromDbmgr',
    'onBroadcastGlobalDataChanged',
    'onCreateCellEntityFromBaseapp',

    'onRegisterNewApp',
]