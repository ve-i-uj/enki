"""The Interfaces component мessages (not generated)."""

from enki.kbeenum import ComponentType
from enki.kbetype import *
from enki.msg.msg_descr import FIXED, VARIABLE, MsgDescr

from . import custom

lookApp = MsgDescr(  # noqa: N816
    id=12,
    lenght=-1,
    name="Interfaces::lookApp",
    args_type=FIXED,
    args=(),
    desc="Check the component is alive",
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name="Interfaces::onRegisterNewApp",
    args_type=FIXED,
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
    id=55104,
    lenght=12,
    name="Interfaces::onAppActiveTick",
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc="Компонент сообщает, что он живой",
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name="Interfaces::reqCloseServer",
    args_type=VARIABLE,
    args=(),
    desc="Отправить сигнал компоненту, что ему нужно остановиться",
)

onAccountLogin = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name="Interfaces::onAccountLogin",
    args_type=VARIABLE,
    args=(
        UINT64,  # component_id
        STRING,  # login
        STRING,  # password
        BLOB,  # data
    ),
    desc="Проброс вызова из DBMgr на Interfaces",
)

reqCreateAccount = MsgDescr(  # noqa: N816
    id=9,
    lenght=-1,
    name="Interfaces::reqCreateAccount",
    args_type=VARIABLE,
    args=(
        COMPONENT_ID,  # component_id
        STRING,  # registerName
        STRING,  # password
        UINT8,  # accountType
        BLOB,  # datas
    ),
    desc="Запрос на создание нового аккаунта",
)

charge = MsgDescr(
    id=11,
    lenght=-1,
    name="Interfaces::charge",
    args_type=VARIABLE,
    args=(
        STRING,  # orderID
        UINT32,  # dbid
        STRING,  # accountName
        UINT32,  # gold
    ),
    desc="Информация о платеже/пополнении счета",
)

eraseClientReq = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name="Interfaces::eraseClientReq",
    args_type=VARIABLE,
    args=(
        UINT32,  # dbid
        STRING,  # accountName
    ),
    desc="Запрос на удаление аккаунта клиента",
)

reqKillServer = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name="Interfaces::reqKillServer",
    args_type=VARIABLE,
    args=(
        STRING,  # componentType
        UINT64,  # componentID
    ),
    desc="Принудительное завершение компонента сервера",
)

onExecuteRawDatabaseCommandCB = MsgDescr(  # noqa: N816
    id=17,
    lenght=-1,
    name="Interfaces::onExecuteRawDatabaseCommandCB",
    args_type=VARIABLE,
    args=(
        UINT32,  # id
        BLOB,  # result
    ),
    desc="Callback с результатом выполнения сырого SQL-запроса",
)

queryWatcher = MsgDescr(  # noqa: N816
    id=41007,
    lenght=-1,
    name="Interfaces::queryWatcher",
    args_type=VARIABLE,
    args=(STRING,),  # path
    desc="Запрос значения watcher по указанному пути",
)


onLookApp = custom.change_component_owner(  # noqa: N816
    custom.onLookApp, ComponentType.INTERFACES
)
onReqCloseServer = custom.change_component_owner(  # noqa: N816
    custom.onReqCloseServer, ComponentType.INTERFACES
)


SPEC_BY_ID = {
    onAccountLogin.id: onAccountLogin,
    lookApp.id: lookApp,
    onLookApp.id: onLookApp,
    onReqCloseServer.id: onReqCloseServer,
    onRegisterNewApp.id: onRegisterNewApp,
    reqCloseServer.id: reqCloseServer,
    onAppActiveTick.id: onAppActiveTick,
    reqCreateAccount.id: reqCreateAccount,
    charge.id: charge,
    eraseClientReq.id: eraseClientReq,
    reqKillServer.id: reqKillServer,
    onExecuteRawDatabaseCommandCB.id: onExecuteRawDatabaseCommandCB,
    queryWatcher.id: queryWatcher,
    # KBEngine одно и тоже сообщение гоняет, не меняя отправителя (скорей всего баг)
    55105: onAppActiveTick,
}

__all__ = [
    "SPEC_BY_ID",
    "charge",
    "eraseClientReq",
    "lookApp",
    "onAccountLogin",
    "onAppActiveTick",
    "onExecuteRawDatabaseCommandCB",
    "onLookApp",
    "onRegisterNewApp",
    "onReqCloseServer",
    "queryWatcher",
    "reqCloseServer",
    "reqCreateAccount",
    "reqKillServer",
]
