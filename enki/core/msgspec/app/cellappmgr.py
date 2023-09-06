"""The DBMgr component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


onAppActiveTick = MsgDescr(
    id=55102,
    lenght=12,
    name='CellappMgr::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

lookApp = MsgDescr(
    id=9,
    lenght=-1,
    name='CellappMgr::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name='CellappMgr::onRegisterNewApp',
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

updateCellapp = MsgDescr(
    id=15,
    lenght=20,
    name='CellappMgr::updateCellapp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_ID,  # componentID
        kbetype.ENTITY_ID,  # numEntities
        kbetype.FLOAT,  # load
        kbetype.UINT32,  # flags
    ]),
    desc='Update cellapp information'
)

reqCreateCellEntityInNewSpace = MsgDescr(
    id=11,
    lenght=-1,
    name='CellappMgr::reqCreateCellEntityInNewSpace',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

updateSpaceData = MsgDescr(
    id=19,
    lenght=-1,
    name='CellappMgr::updateSpaceData',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.COMPONENT_ID,  # componentID
        kbetype.SPACE_ID,  # spaceID
        kbetype.STRING,  # scriptModuleName
        kbetype.BOOL,  # delspace
        kbetype.STRING,  # geomappingPath
    ]),
    desc=''
)

reqCloseServer = MsgDescr(
    id=14,
    lenght=-1,
    name='CellappMgr::reqCloseServer',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple(),
    desc='Отправить сигнал компоненту, что ему нужно остановиться'
)

SPEC_BY_ID = {
    onAppActiveTick.id: onAppActiveTick,
    lookApp.id: lookApp,
    onRegisterNewApp.id: onRegisterNewApp,
    updateCellapp.id: updateCellapp,
    reqCreateCellEntityInNewSpace.id: reqCreateCellEntityInNewSpace,
    updateSpaceData.id: updateSpaceData,
    reqCloseServer.id: reqCloseServer,
}

__all__ = [
    'SPEC_BY_ID',
    'onAppActiveTick',
    'lookApp',
    'onRegisterNewApp',
    'updateCellapp',
    'reqCreateCellEntityInNewSpace',
    'updateSpaceData',
    'reqCloseServer',
]