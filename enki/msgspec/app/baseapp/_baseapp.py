"""Messages of BaseApp."""

from enki import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


hello = MsgDescr(  # noqa: N816
    id=200,
    lenght=-1,
    name='BaseApp::hello',
    args_type=VARIABLE,
    args=(
        STRING,  # server version
        STRING,  # assets version
        BLOB,    # encrypted key
    ),
    desc='hello'
)

importClientMessages = MsgDescr(  # noqa: N816
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=FIXED,
    args=(),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = MsgDescr(  # noqa: N816
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=FIXED,
    args=(),
    desc='TCPClient entitydef export.'
)

onUpdateDataFromClient = MsgDescr(  # noqa: N816
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=VARIABLE,
    args=(
        FLOAT,
        FLOAT,
        FLOAT,
        FLOAT,
        FLOAT,
        FLOAT,
        BOOL,
        SPACE_ID,
    ),
    desc=''
)

onUpdateDataFromClientForControlledEntity = MsgDescr(  # noqa: N816
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=VARIABLE,
    args=(
        ENTITY_ID,
        FLOAT,
        FLOAT,
        FLOAT,
        FLOAT,
        FLOAT,
        FLOAT,
        BOOL,
        SPACE_ID,
    ),
    desc=''
)

lookApp = MsgDescr(  # noqa: N816
    id=8,
    lenght=-1,
    name='Baseapp::lookApp',
    args_type=FIXED,
    args=(),
    desc='Check the component is alive'
)

onCreateEntityAnywhere = MsgDescr(  # noqa: N816
    id=16,
    lenght=-1,
    name='Baseapp::onCreateEntityAnywhere',
    args_type=FIXED,
    args=(
        UINT8_ARRAY  # см. обработчик
    )
    desc='Создать сущность на наименее этом Baseapp'
)

onGetEntityAppFromDbmgr = MsgDescr(  # noqa: N816
    id=11,
    lenght=-1,
    name='Baseapp::onGetEntityAppFromDbmgr',
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
    desc=''
)

onDbmgrInitCompleted = MsgDescr(  # noqa: N816
    id=13,
    lenght=-1,
    name='Baseapp::onDbmgrInitCompleted',
    args_type=VARIABLE,
    args=(
        GAME_TIME,  # gametime
        ENTITY_ID,  # startID
        ENTITY_ID,  # endID
        COMPONENT_ORDER,  # startGlobalOrder
        COMPONENT_ORDER,  # startGroupOrder
        STRING,  # digest
    ),
    desc=''
)

onEntityAutoLoadCBFromDBMgr = MsgDescr(  # noqa: N816
    id=23,
    lenght=-1,
    name='Baseapp::onEntityAutoLoadCBFromDBMgr',
    args_type=VARIABLE,
    args=(
        UINT8_ARRAY,
    ),
    desc='Информация об автоматической загрузке сущности, возвращаемая запросом из базы данных'
)

onBroadcastGlobalDataChanged = MsgDescr(  # noqa: N816
    id=14,
    lenght=-1,
    name='Baseapp::onBroadcastGlobalDataChanged',
    args_type=VARIABLE,
    args=(
        UINT8_ARRAY,
    ),
    desc=''
)

onAppActiveTick = MsgDescr(  # noqa: N816
    id=55100,
    lenght=12,
    name='Baseapp::onAppActiveTick',
    args_type=FIXED,
    args=(
        COMPONENT_TYPE,  # componentType
        COMPONENT_ID,  # componentID
    ),
    desc='Компонент сообщает, что он живой'
)

onRegisterNewApp = MsgDescr(  # noqa: N816
    id=10,
    lenght=-1,
    name='Baseapp::onRegisterNewApp',
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

onEntityGetCell = MsgDescr(  # noqa: N816
    id=20,
    lenght=4+8+4,
    name='Baseapp::onEntityGetCell',
    args_type=FIXED,
    args=(
        ENTITY_ID,  # entity_id
        COMPONENT_ID,  # componentID
        SPACE_ID,  # spaceID
    ),
    desc='???'
)

reqCloseServer = MsgDescr(  # noqa: N816
    id=34,
    lenght=-1,
    name='Baseapp::reqCloseServer',
    args_type=VARIABLE,
    args=(),
    desc='Отправить сигнал компоненту, что ему нужно остановиться'
)

SPEC_BY_ID = {
    hello.id: hello,
    importClientMessages.id: importClientMessages,
    importClientEntityDef.id: importClientEntityDef,
    onUpdateDataFromClient.id: onUpdateDataFromClient,
    onUpdateDataFromClientForControlledEntity.id: onUpdateDataFromClientForControlledEntity,

    lookApp.id: lookApp,
    onCreateEntityAnywhere.id: onCreateEntityAnywhere,
    onGetEntityAppFromDbmgr.id: onGetEntityAppFromDbmgr,
    onDbmgrInitCompleted.id: onDbmgrInitCompleted,
    onEntityAutoLoadCBFromDBMgr.id: onEntityAutoLoadCBFromDBMgr,
    onBroadcastGlobalDataChanged.id: onBroadcastGlobalDataChanged,
    onAppActiveTick.id: onAppActiveTick,
    onRegisterNewApp.id: onRegisterNewApp,
    onEntityGetCell.id: onEntityGetCell,
    reqCloseServer.id: reqCloseServer,
}


__all__ = [
    'SPEC_BY_ID',
    'hello',
    'importClientMessages',
    'importClientEntityDef',
    'onUpdateDataFromClient',
    'onUpdateDataFromClientForControlledEntity',

    'lookApp',
    'onCreateEntityAnywhere',
    'onGetEntityAppFromDbmgr',
    'onDbmgrInitCompleted',
    'onEntityAutoLoadCBFromDBMgr',
    'onBroadcastGlobalDataChanged',
    'onAppActiveTick',
    'onRegisterNewApp',
    'onEntityGetCell',

    'reqCloseServer',
]
