"""The DBMgr component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import FLOAT, INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.basic_data_type_decoders import (
    BOOL,
    INT8,
    UINT8_ARRAY,
)
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


queryLoad = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="CellappMgr::queryLoad",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # componentID
        STRING,  # componentType
    ),
    desc="Запрос информации о загрузке компонента (используется для балансировки нагрузки)",
)

reqRestoreSpaceInCell = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="CellappMgr::reqRestoreSpaceInCell",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # componentID
        SPACE_ID,  # spaceID
        STRING,  # scriptModuleName
    ),
    desc="Запрос на восстановление пространства в определенном Cellapp (после перезапуска)",
)

forwardMessage = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="CellappMgr::forwardMessage",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # targetComponentID
        UINT32,  # msgID
        UINT32,  # msgLength
        UINT8_ARRAY,  # msgData
    ),
    desc="Перенаправление сообщения другому компоненту через Cellappmgr",
)

startProfile = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="CellappMgr::startProfile",
    args_type=VARIABLE,
    args=(
        STRING,  # profileName
        INT8,  # profileType
        UINT32,  # timelen
    ),
    desc="Запуск или остановка профилирования на компонентах",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="CellappMgr::reqKillServer",
    args_type=VARIABLE,
    args=(),
    desc="Запрос на немедленную остановку компонента (kill signal)",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41005,
    lenght=-1,
    name="CellappMgr::queryWatcher",
    args_type=VARIABLE,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        UINT32,  # uid
        STRING,  # username
        STRING,  # watcherPath
    ),
    desc="Запрос данных мониторинга (watcher) у компонента",
)

queryAppsLoads = MsgDescr(  # noqa: N816
    id=50002,
    lenght=-1,
    name="CellappMgr::queryAppsLoads",
    args_type=VARIABLE,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        UINT32,  # uid
        STRING,  # username
    ),
    desc="Запрос информации о загрузке всех приложений (Cellapps)",
)

querySpaces = MsgDescr(  # noqa: N816
    id=50003,
    lenght=-1,
    name="CellappMgr::querySpaces",
    args_type=VARIABLE,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        UINT32,  # uid
        STRING,  # username
    ),
    desc="Запрос информации о всех пространствах (spaces), управляемых Cellappmgr",
)

setSpaceViewer = MsgDescr(  # noqa: N816
    id=50004,
    lenght=-1,
    name="CellappMgr::setSpaceViewer",
    args_type=VARIABLE,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        UINT32,  # uid
        STRING,  # username
        SPACE_ID,  # spaceID
        ENTITY_ID,  # viewerID
    ),
    desc="Установка наблюдателя (viewer) для пространства",
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
    queryLoad.id: queryLoad,
    reqRestoreSpaceInCell.id: reqRestoreSpaceInCell,
    forwardMessage.id: forwardMessage,
    startProfile.id: startProfile,
    reqKillServer.id: reqKillServer,
    queryWatcher.id: queryWatcher,
    queryAppsLoads.id: queryAppsLoads,
    querySpaces.id: querySpaces,
    setSpaceViewer.id: setSpaceViewer,
}

__all__ = [
    "SPEC_BY_ID",
    "forwardMessage",
    "lookApp",
    "onAppActiveTick",
    "onCellappInitProgress",
    "onLookApp",
    "onRegisterNewApp",
    "onReqCloseServer",
    "queryAppsLoads",
    "queryLoad",
    "querySpaces",
    "queryWatcher",
    "reqCloseServer",
    "reqCreateCellEntityInNewSpace",
    "reqKillServer",
    "reqRestoreSpaceInCell",
    "setSpaceViewer",
    "startProfile",
    "updateCellapp",
    "updateSpaceData",
]
