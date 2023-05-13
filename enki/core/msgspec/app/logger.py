"""The Logger component мessages (not generated)."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


queryLoad = MsgDescr(
    id=705,
    lenght=0,
    name='Logger::queryLoad',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='(?) Check the component is alive'
)

writeLog = MsgDescr(
    id=704,
    lenght=-1,
    name='Logger::writeLog',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.INT32,  # uid
        kbetype.UINT32,  # logtype
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
        kbetype.COMPONENT_ORDER,  # globalOrder
        kbetype.COMPONENT_ORDER,  # groupOrder
        kbetype.INT64,  # time
        kbetype.UINT32,  # kbetime
        kbetype.ENDLESS_BLOB,  # log size and msg
    ]),
    desc='Отправить логи по TCP'
)

onRegisterNewApp = MsgDescr(
    id=8,
    lenght=-1,
    name='Logger::onRegisterNewApp',
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
    queryLoad.id: queryLoad,
    writeLog.id: writeLog,
    onRegisterNewApp.id: onRegisterNewApp,
}
