"""The DBMgr component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import INT32, STRING, UINT16, UINT32
from enki.kbetype.decoders.basic_data_type_decoders import (
    BLOB,
    UINT64,
    UINT8_ARRAY,
)
from enki.kbetype.decoders.custom_decoders import (
    COMPONENT_ID,
    COMPONENT_ORDER,
    COMPONENT_TYPE,
    ENTITY_ID,
)
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

from . import custom

lookApp = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="DBMgr::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="DBMgr::onRegisterNewApp",
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

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55105,
    lenght=12,
    name="DBMgr::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

onBroadcastGlobalDataChanged = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="DBMgr::onBroadcastGlobalDataChanged",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

syncEntityStreamTemplate = MsgDescr(  # noqa: N816
    id=29,
    lenght=-1,
    name="DBMgr::syncEntityStreamTemplate",
    args_type=VARIABLE,
    args=(UINT8_ARRAY,),
    desc="",
)

entityAutoLoad = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name="DBMgr::entityAutoLoad",
    args_type=VARIABLE,
    args=(
        UINT16,  # dbInterfaceIndex
        COMPONENT_ID,  # componentID
        UINT16,  # entityType
        ENTITY_ID,  # start
        ENTITY_ID,  # end
    ),
    desc="",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=26,
    lenght=-1,
    name="DBMgr::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

onAccountLogin = MsgDescr(  # noqa: N816
    id=15,
    lenght=-1,
    name="DBMgr::onAccountLogin",
    args_type=VARIABLE,
    args=(
        STRING,  # login
        STRING,  # password
        BLOB,  # data
    ),
    desc="Проброс вызова из Loginapp на DBMgr",
)

onLoginAccountCBBFromInterfaces = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="DBMgr::onLoginAccountCBBFromInterfaces",
    args_type=VARIABLE,
    args=(
        UINT64,  # component_id
        STRING,  # login
        STRING,  # account_name
        STRING,  # password
        UINT16,  # ret_code
        STRING,  # postdatas
        STRING,  # getdatas
    ),
    desc="Ответ от Interfaces на DBMgr",
)


onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.DBMGR
)
onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.DBMGR
)

SPEC_BY_ID = {
    lookApp.id: lookApp,
    onLookApp.id: onLookApp,
    onRegisterNewApp.id: onRegisterNewApp,
    onAppActiveTick.id: onAppActiveTick,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    syncEntityStreamTemplate.id: syncEntityStreamTemplate,
    entityAutoLoad.id: entityAutoLoad,
    reqCloseServer.id: reqCloseServer,
    onReqCloseServer.id: onReqCloseServer,
    onAccountLogin.id: onAccountLogin,
    onLoginAccountCBBFromInterfaces.id: onLoginAccountCBBFromInterfaces,
}

__all__ = [
    "SPEC_BY_ID",
    "entityAutoLoad",
    "lookApp",
    "onAccountLogin",
    "onAppActiveTick",
    "onBroadcastGlobalDataChanged",
    "onLoginAccountCBBFromInterfaces",
    "onLookApp",
    "onRegisterNewApp",
    "onReqCloseServer",
    "reqCloseServer",
    "syncEntityStreamTemplate",
]
