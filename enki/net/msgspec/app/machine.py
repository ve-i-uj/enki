"""The Machine component мessages (not generated)."""

from enki import kbeenum, settings
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.message import MsgDescr


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

# Это пользовательское сообщение для парсинга ответа на onQueryAllInterfaceInfos.
# На это сообщение ответ приходит не в виде сообщения а сразу в виде данных
resp_onQueryAllInterfaceInfos = MsgDescr(
    id=settings.NO_ID,
    lenght=-1,
    name='Machine::resp_onQueryAllInterfaceInfos',
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
        kbetype.UINT16,  # backRecvPort
    ),
    desc='User defined message'
)

SPEC_BY_ID = {
    onQueryAllInterfaceInfos.id: onQueryAllInterfaceInfos,
    resp_onQueryAllInterfaceInfos.id: resp_onQueryAllInterfaceInfos,
}
