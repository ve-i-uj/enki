"""The Logger component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import (
    INT8,
    INT32,
    INT64,
    STRING,
    UINT8,
    UINT8_ARRAY,
    UINT16,
    UINT32,
)
from enki.kbetype.decoders.basic_data_type_decoders import BLOB, UINT64
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr, MsgSpecById

from . import custom

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="Logger::onRegisterNewApp",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        STRING,  # username
        INT32,  # componentType
        UINT64,  # componentID
        INT32,  # globalorderID
        INT32,  # grouporderID
        UINT32,  # intaddr
        UINT16,  # intport
        UINT32,  # extaddr
        UINT16,  # extport
        STRING,  # extaddrEx
    ),
    desc="Notify component about itself",
)

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="Logger::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

queryLoad = MsgDescr(  # noqa: N816
    id=10,
    lenght=0,
    name="Logger::queryLoad",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

updateLogWatcherSetting = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="Logger::updateLogWatcherSetting",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        UINT32,  # logtypes filter
        COMPONENT_ORDER,  # globalOrder
        COMPONENT_ORDER,  # groupOrder
        STRING,  # date
        STRING,  # keyStr
        UINT8_ARRAY,  # component type filter (массив UINT8)
    ),
    desc="Update watcher settings",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Logger::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Send signal to component to stop",
)

startProfile = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Logger::startProfile",
    args_type=VARIABLE,
    args=(
        STRING,  # profileName
        INT8,  # profileType
        UINT32,  # timelen
    ),
    desc="Start performance profiling",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Logger::reqKillServer",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # component_id
        COMPONENT_TYPE,  # componentType
        STRING,  # username
        INT32,  # uid
        STRING,  # reason
    ),
    desc="Request to forcibly stop the server",
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=701,
    lenght=12,
    name="Logger::onAppActiveTick",
    args_type=FIXED,
    args=(
        INT32,  # componentType
        UINT64,  # componentID
    ),
    desc="Component reports that it is alive",
)

registerLogWatcher = MsgDescr(  # noqa: N816
    id=702,
    lenght=-1,
    name="Logger::registerLogWatcher",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        UINT32,  # logtypes filter
        INT32,  # globalOrder
        INT32,  # groupOrder
        STRING,  # date
        STRING,  # keyStr
        UINT8_ARRAY,  # component type filter (массив UINT8)
        UINT8,  # isfind
        UINT8,  # first
    ),
    desc="Register a watcher",
)

deregisterLogWatcher = MsgDescr(  # noqa: N816
    id=703,
    lenght=-1,
    name="Logger::deregisterLogWatcher",
    args_type=VARIABLE,
    args=(),
    desc="Unregister a watcher",
)

writeLog = MsgDescr(  # noqa: N816
    id=704,
    lenght=-1,
    name="Logger::writeLog",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        UINT32,  # logtype
        INT32,  # componentType
        UINT64,  # componentID
        INT32,  # globalOrder
        INT32,  # groupOrder
        INT64,  # time
        UINT32,  # kbetime
        BLOB,  # log size and msg
    ),
    desc="Send logs via TCP",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41008,
    lenght=-1,
    name="Logger::queryWatcher",
    args_type=VARIABLE,
    args=(STRING,),  # path
    desc="Query watcher",
)

onLookApp = custom.change_component_owner(
    custom.onLookApp, ComponentType.LOGGER
)
onReqCloseServer = custom.change_component_owner(
    custom.onReqCloseServer, ComponentType.LOGGER
)

SPEC_BY_ID: MsgSpecById = {
    deregisterLogWatcher.id: deregisterLogWatcher,
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    onLookApp.id: onLookApp,
    onRegisterNewApp.id: onRegisterNewApp,
    onReqCloseServer.id: onReqCloseServer,
    queryLoad.id: queryLoad,
    queryWatcher.id: queryWatcher,
    registerLogWatcher.id: registerLogWatcher,
    reqCloseServer.id: reqCloseServer,
    reqKillServer.id: reqKillServer,
    startProfile.id: startProfile,
    updateLogWatcherSetting.id: updateLogWatcherSetting,
    writeLog.id: writeLog,
}

__all__ = [
    "SPEC_BY_ID",
    "deregisterLogWatcher",
    "lookApp",
    "onAppActiveTick",
    "onLookApp",
    "onRegisterNewApp",
    "onReqCloseServer",
    "queryLoad",
    "queryWatcher",
    "registerLogWatcher",
    "reqCloseServer",
    "reqKillServer",
    "startProfile",
    "updateLogWatcherSetting",
    "writeLog",
]
