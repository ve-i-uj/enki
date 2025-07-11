"""The Machine component мessages (not generated)."""

from enki.kbetype import FLOAT, INT8, INT32, STRING, UINT16, UINT32, UINT64
from enki.decoders.custom_decoders import (
    COMPONENT_GUS,
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    UINT8_ARRAY,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

onQueryAllInterfaceInfos = MsgDescr(  # noqa: N816
    id=4,
    lenght=-1,
    name="Machine::onQueryAllInterfaceInfos",
    args_type=VARIABLE,
    args=(
        INT32,
        STRING,
        UINT16,
    ),
    desc="",
)

lookApp = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="Machine::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onBroadcastInterface = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="Machine::onBroadcastInterface",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        STRING,  # username
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_ID,  # componentIDEx
        COMPONENT_ORDER,  # globalorderid
        COMPONENT_ORDER,  # grouporderid
        COMPONENT_GUS,  # gus
        UINT32,  # intaddr
        UINT16,  # intport
        UINT32,  # extaddr
        UINT16,  # extport
        STRING,  # extaddrEx
        UINT32,  # pid
        FLOAT,  # cpu
        FLOAT,  # mem
        UINT32,  # usedmem
        INT8,  # state
        UINT32,  # machineID
        UINT64,  # extradata
        UINT64,  # extradata1
        UINT64,  # extradata2
        UINT64,  # extradata3
        UINT32,  # backRecvAddr
        UINT16,  # backRecvPort
    ),
    desc="Статистика компонента",
)

onFindInterfaceAddr = MsgDescr(  # noqa: N816
    id=1,
    lenght=-1,
    name="Machine::onFindInterfaceAddr",
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        STRING,  # username
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_TYPE,  # findComponentType
        UINT32,  # addr
        UINT16,  # finderRecvPort
    ),
    desc="Запрос найти нужный компонент",
)

queryComponentID = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="Machine::queryComponentID",
    args_type=VARIABLE,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        INT32,  # uid
        UINT16,  # finderRecvPort
        INT32,  # macMD5
        INT32,  # pid
    ),
    desc=(
        "Запросить внутренний id компонента у Машины (ответ отправляется без "
        'обёртки в сообщения на порт "finderRecvPort")'
    ),
)

queryLoad = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name="Machine::queryLoad",
    args_type=FIXED,
    args=(UINT8_ARRAY,),
    desc="Пустое тело в KBEngine у всех компонентов",
)

startserver = MsgDescr(
    id=2,
    lenght=-1,
    name="Machine::startserver",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Not implemented",
)

stopserver = MsgDescr(
    id=3,
    lenght=-1,
    name="Machine::stopserver",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Not implemented",
)

killserver = MsgDescr(
    id=6,
    lenght=-1,
    name="Machine::killserver",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Not implemented",
)

setflags = MsgDescr(
    id=7,
    lenght=-1,
    name="Machine::setflags",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Not implemented",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Machine::reqKillServer",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="Not implemented",
)

SPEC_BY_ID = {
    onQueryAllInterfaceInfos.id: onQueryAllInterfaceInfos,
    queryComponentID.id: queryComponentID,
    lookApp.id: lookApp,
    onBroadcastInterface.id: onBroadcastInterface,
    onFindInterfaceAddr.id: onFindInterfaceAddr,
    queryLoad.id: queryLoad,
    startserver.id: startserver,
    stopserver.id: stopserver,
    killserver.id: killserver,
    setflags.id: setflags,
    reqKillServer.id: reqKillServer,
}

__all__ = [
    "SPEC_BY_ID",
    "killserver",
    "lookApp",
    "onBroadcastInterface",
    "onFindInterfaceAddr",
    "onQueryAllInterfaceInfos",
    "queryComponentID",
    "queryComponentID",
    "queryLoad",
    "reqKillServer",
    "setflags",
    "startserver",
    "stopserver",
]
