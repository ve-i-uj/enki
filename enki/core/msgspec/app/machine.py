"""The Machine component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


onQueryAllInterfaceInfos = MsgDescr(
    id=4,
    lenght=-1,
    name='Machine::onQueryAllInterfaceInfos',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.INT32,
        kbetype.STRING,
        kbetype.UINT16,
    ),
    desc=''
)

lookApp = MsgDescr(
    id=10,
    lenght=-1,
    name='Machine::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

onBroadcastInterface = MsgDescr(
    id=8,
    lenght=-1,
    name='Machine::onBroadcastInterface',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.INT32,  # uid
        kbetype.STRING,  # username
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.COMPONENT_ID,  # componentIDEx
        kbetype.COMPONENT_ORDER,  # globalorderid
        kbetype.COMPONENT_ORDER,  # grouporderid
        kbetype.COMPONENT_GUS,  # gus
        kbetype.UINT32,  # intaddr
        kbetype.UINT16,  # intport
        kbetype.UINT32,  # extaddr
        kbetype.UINT16,  # extport
        kbetype.STRING,  # extaddrEx
        kbetype.UINT32,  # pid
        kbetype.FLOAT,  # cpu
        kbetype.FLOAT,  # mem
        kbetype.UINT32,  # usedmem
        kbetype.INT8,  # state
        kbetype.UINT32,  # machineID
        kbetype.UINT64,  # extradata
        kbetype.UINT64,  # extradata1
        kbetype.UINT64,  # extradata2
        kbetype.UINT64,  # extradata3
        kbetype.UINT32,  # backRecvAddr
        kbetype.UINT16  # backRecvPort
    ),
    desc='Статистика компонента'
)

onFindInterfaceAddr = MsgDescr(
    id=1,
    lenght=-1,
    name='Machine::onFindInterfaceAddr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.INT32,  # uid
        kbetype.STRING,  # username
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.COMPONENT_TYPE,  # findComponentType
        kbetype.UINT32,  # addr
        kbetype.UINT16,  # finderRecvPort
    ),
    desc='Запрос найти нужный компонент'
)

queryComponentID = MsgDescr(
    id=9,
    lenght=-1,
    name='Machine::queryComponentID',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.INT32,  # uid
        kbetype.UINT16,  # finderRecvPort
        kbetype.INT32,  # macMD5
        kbetype.INT32,  # pid
    ),
    desc='Запросить внутренний id компонента у Машины (ответ отправляется без обёртки в сообщения на порт "finderRecvPort")'
)

queryLoad = MsgDescr(
    id=11,
    lenght=-1,
    name='Machine::queryLoad',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Пустое тело в KBEngine у всех компонентов'
)

startserver = MsgDescr(
    id=2,
    lenght=-1,
    name='Machine::startserver',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Not implemented'
)

stopserver = MsgDescr(
    id=3,
    lenght=-1,
    name='Machine::stopserver',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Not implemented'
)

killserver = MsgDescr(
    id=6,
    lenght=-1,
    name='Machine::killserver',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Not implemented'
)

setflags = MsgDescr(
    id=7,
    lenght=-1,
    name='Machine::setflags',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Not implemented'
)

reqKillServer = MsgDescr(
    id=12,
    lenght=-1,
    name='Machine::reqKillServer',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Not implemented'
)

SPEC_BY_ID = {
    onQueryAllInterfaceInfos.id: onQueryAllInterfaceInfos,

    queryComponentID.id: queryComponentID,

    lookApp.id: lookApp,

    onBroadcastInterface.id: onBroadcastInterface,
    onFindInterfaceAddr.id: onFindInterfaceAddr,
    queryComponentID.id: queryComponentID,

    queryLoad.id: queryLoad,
    startserver.id: startserver,
    stopserver.id: stopserver,
    killserver.id: killserver,
    setflags.id: setflags,
    reqKillServer.id: reqKillServer,
}

__all__ = [
    'SPEC_BY_ID',
    'onQueryAllInterfaceInfos',
    'queryComponentID',
    'lookApp',
    'onBroadcastInterface',
    'onFindInterfaceAddr',
    'queryComponentID',

    'queryLoad',
    'startserver',
    'stopserver',
    'killserver',
    'setflags',
    'reqKillServer',
]
