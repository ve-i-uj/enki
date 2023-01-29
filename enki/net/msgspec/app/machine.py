"""The Machine component мessages (not generated)."""

from enki import kbeenum
from enki.net.kbeclient import kbetype
from enki.net.kbeclient.message import MsgDescr

from .. import internal


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
fakeRespOnQueryAllInterfaceInfos = MsgDescr(
    id=internal.get_fake_msg_id(),
    lenght=-1,
    name='Enki::fakeRespOnQueryAllInterfaceInfos',
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

# TODO: [2023-01-28 12:14 burov_alexey@mail.ru]:
# Насколько понял, он вернёт токен (среди прочих данных), по которому
# у Машины можно запрашивать данные
queryComponentID = MsgDescr(
    id=6,
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

fakeRespLookApp = MsgDescr(
    id=internal.get_fake_msg_id(),
    lenght=9,
    name='Enki::fakeRespLookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=(
        kbetype.COMPONENT_TYPE,
        kbetype.COMPONENT_ID,
        kbetype.INT8
    ),
    desc='The fake message contained the serialization specification'
)


SPEC_BY_ID = {
    onQueryAllInterfaceInfos.id: onQueryAllInterfaceInfos,
    fakeRespOnQueryAllInterfaceInfos.id: fakeRespOnQueryAllInterfaceInfos,

    queryComponentID.id: queryComponentID,

    lookApp.id: lookApp,
    fakeRespLookApp.id: fakeRespLookApp,
}
