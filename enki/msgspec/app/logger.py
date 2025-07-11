"""The Logger component мessages (not generated)."""

from enki import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


queryLoad = MsgDescr(  # noqa: N816
    id=705,
    lenght=0,
    name='Logger::queryLoad',
    args_type=FIXED,
    args=(),
    desc='(?) Check the component is alive'
)

writeLog = MsgDescr(  # noqa: N816
    id=704,
    lenght=-1,
    name='Logger::writeLog',
    args_type=VARIABLE,
    args=(
        INT32,  # uid
        UINT32,  # logtype
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
        COMPONENT_ORDER,  # globalOrder
        COMPONENT_ORDER,  # groupOrder
        INT64,  # time
        UINT32,  # kbetime
        ENDLESS_BLOB,  # log size and msg
    ),
    desc='Отправить логи по TCP'
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name='Logger::onRegisterNewApp',
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
    desc='???'
)

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name='Logger::lookApp',
    args_type=FIXED,
    args=(),
    desc='Check the component is alive'
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=701,
    lenght=12,
    name='DBMgr::onAppActiveTick',
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc='Компонент сообщает, что он живой'
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name='Logger::reqCloseServer',
    args_type=VARIABLE,
    args=(),
    desc='Отправить сигнал компоненту, что ему нужно остановиться'
)

SPEC_BY_ID = {
    queryLoad.id: queryLoad,
    writeLog.id: writeLog,
    onRegisterNewApp.id: onRegisterNewApp,
    lookApp.id: lookApp,
    onAppActiveTick.id: onAppActiveTick,
    reqCloseServer.id: reqCloseServer,
}

__all__ = [
    'SPEC_BY_ID',
    'queryLoad',
    'writeLog',
    'onRegisterNewApp',
    'lookApp',
    'onAppActiveTick',
    'reqCloseServer',
]