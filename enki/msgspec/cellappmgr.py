"""The DBMgr component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import FLOAT, INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.basic_data_type_decoders import BOOL, UINT8_ARRAY
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    ENTITY_ID,
    SPACE_ID,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

from . import custom

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="CellappMgr::onRegisterNewApp",
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

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="CellappMgr::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

reqCreateCellEntityInNewSpace = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="CellappMgr::reqCreateCellEntityInNewSpace",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55102,
    lenght=12,
    name="CellappMgr::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="CellappMgr::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

updateCellapp = MsgDescr(  # noqa: N816
    id=15,
    lenght=20,
    name="CellappMgr::updateCellapp",
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # componentID
        ENTITY_ID,  # numEntities
        FLOAT,  # load
        UINT32,  # flags
    ),
    desc="Update cellapp information",
)

onCellappInitProgress = MsgDescr(  # noqa: N816
    id=18,
    lenght=24,
    name="CellappMgr::onCellappInitProgress",
    args_type=FIXED,
    args=(
        COMPONENT_ID,  # cid - ID компонента (UINT64, 8 байт)
        FLOAT,  # progress - прогресс инициализации (double, 8 байт)
        COMPONENT_ORDER,  # componentGlobalOrder (INT32, 4 байта)
        COMPONENT_ORDER,  # componentGroupOrder (INT32, 4 байта)
    ),
    desc="Cellapp сообщает о прогрессе своей инициализации",
)

updateSpaceData = MsgDescr(  # noqa: N816
    id=19,
    lenght=-1,
    name="CellappMgr::updateSpaceData",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # componentID
        SPACE_ID,  # spaceID
        STRING,  # scriptModuleName
        BOOL,  # delspace
        STRING,  # geomappingPath
    ),
    desc="",
)


onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.CELLAPPMGR
)

onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.CELLAPPMGR
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    onLookApp.id: onLookApp,
    onAppActiveTick.id: onAppActiveTick,
    onRegisterNewApp.id: onRegisterNewApp,
    updateCellapp.id: updateCellapp,
    reqCreateCellEntityInNewSpace.id: reqCreateCellEntityInNewSpace,
    updateSpaceData.id: updateSpaceData,
    reqCloseServer.id: reqCloseServer,
    onReqCloseServer.id: onReqCloseServer,
    onCellappInitProgress.id: onCellappInitProgress,
}

__all__ = [
    "SPEC_BY_ID",
    "lookApp",
    "onAppActiveTick",
    "onLookApp",
    "onRegisterNewApp",
    "onReqCloseServer",
    "reqCloseServer",
    "reqCreateCellEntityInNewSpace",
    "updateCellapp",
    "updateSpaceData",
]
