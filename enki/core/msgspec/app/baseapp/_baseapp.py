"""Messages of BaseApp."""

from enki.core import kbeenum
from enki.core import kbetype
from enki.core.message import MsgDescr


hello = MsgDescr(
    id=200,
    lenght=-1,
    name='BaseApp::hello',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.STRING,  # server version
        kbetype.STRING,  # assets version
        kbetype.BLOB,    # encrypted key
    ),
    desc='hello'
)

importClientMessages = MsgDescr(
    id=207,
    lenght=0,
    name='Baseapp::importClientMessages',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='The client requests to import the message protocol.'
)

importClientEntityDef = MsgDescr(
    id=208,
    lenght=0,
    name='Baseapp::importClientEntityDef',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple(),
    desc='TCPClient entitydef export.'
)

onUpdateDataFromClient = MsgDescr(
    id=27,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClient',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.BOOL,
        kbetype.SPACE_ID,
    ),
    desc=''
)

onUpdateDataFromClientForControlledEntity = MsgDescr(
    id=28,
    lenght=-1,
    name='Baseapp::onUpdateDataFromClientForControlledEntity',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=(
        kbetype.ENTITY_ID,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.FLOAT,
        kbetype.BOOL,
        kbetype.SPACE_ID,
    ),
    desc=''
)

lookApp = MsgDescr(
    id=8,
    lenght=-1,
    name='Baseapp::lookApp',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
    ]),
    desc='Check the component is alive'
)

onCreateEntityAnywhere = MsgDescr(
    id=16,
    lenght=-1,
    name='Baseapp::onCreateEntityAnywhere',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.UINT8_ARRAY  # см. обработчик
    ]),
    desc='Создать сущность на наименее этом Baseapp'
)

onGetEntityAppFromDbmgr = MsgDescr(
    id=11,
    lenght=-1,
    name='Baseapp::onGetEntityAppFromDbmgr',
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
    desc=''
)

onDbmgrInitCompleted = MsgDescr(
    id=13,
    lenght=-1,
    name='Baseapp::onDbmgrInitCompleted',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.GAME_TIME,  # gametime
        kbetype.ENTITY_ID,  # startID
        kbetype.ENTITY_ID,  # endID
        kbetype.COMPONENT_ORDER,  # startGlobalOrder
        kbetype.COMPONENT_ORDER,  # startGroupOrder
        kbetype.STRING,  # digest
    ]),
    desc=''
)

onEntityAutoLoadCBFromDBMgr = MsgDescr(
    id=23,
    lenght=-1,
    name='Baseapp::onEntityAutoLoadCBFromDBMgr',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc='Информация об автоматической загрузке сущности, возвращаемая запросом в базу данных'
)

onBroadcastGlobalDataChanged = MsgDescr(
    id=14,
    lenght=-1,
    name='Baseapp::onBroadcastGlobalDataChanged',
    args_type=kbeenum.MsgArgsType.VARIABLE,
    field_types=tuple([
        kbetype.UINT8_ARRAY
    ]),
    desc=''
)

onAppActiveTick = MsgDescr(
    id=55100,
    lenght=12,
    name='Baseapp::onAppActiveTick',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.COMPONENT_TYPE,  # componentType
        kbetype.COMPONENT_ID,  # componentID
    ]),
    desc='Компонент сообщает, что он живой'
)

onRegisterNewApp = MsgDescr(
    id=10,
    lenght=-1,
    name='Baseapp::onRegisterNewApp',
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

onEntityGetCell = MsgDescr(
    id=20,
    lenght=4+8+4,
    name='Baseapp::onEntityGetCell',
    args_type=kbeenum.MsgArgsType.FIXED,
    field_types=tuple([
        kbetype.ENTITY_ID,  # entity_id
        kbetype.COMPONENT_ID,  # componentID
        kbetype.SPACE_ID,  # spaceID
    ]),
    desc='???'
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
}
