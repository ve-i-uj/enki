"""Описания KBEngine-сообщений."""

from enki.kbeenum import ComponentType
from enki.msg.msg_descr import ComponentMsgSpecById

from . import (
    baseapp,
    baseappmgr,
    cellapp,
    cellappmgr,
    clientapp,
    custom,
    dbmgr,
    interfaces,
    logger,
    loginapp,
    machine,
    supervisor,
)

# Добим пользовательское сообщение во все компоненты от которых оно будет
# ожидаться. Пользовательского сообщения нет в KBEngine - это механизм для
# ответов именно этой библиотеки. В сообщении описано, как его сериализовать.
# Если нужно только описание сериализации, то настоящий id не нужен. Важно
# только, чтобы сериализатор сообщения мог найти описание [пользовательского]
# сообщения.

machine.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
logger.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
interfaces.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
dbmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
cellappmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
baseappmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
baseapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
cellapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
loginapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp

machine.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
logger.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
interfaces.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
dbmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
cellappmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
baseappmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
baseapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
cellapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
loginapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer


# Для упрощённого доступа к описаниям здесь связывается энам компонента и
# маппинг спецификации сообщений

ClienappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CLIENT, clientapp.SPEC_BY_ID
)
MachineMsgSpecByID = ComponentMsgSpecById(ComponentType.MACHINE, machine.SPEC_BY_ID)
LoggerMsgSpecByID = ComponentMsgSpecById(ComponentType.LOGGER, logger.SPEC_BY_ID)
DBMgrMsgSpecByID = ComponentMsgSpecById(ComponentType.DBMGR, dbmgr.SPEC_BY_ID)
InterfacesMsgSpecByID = ComponentMsgSpecById(
    ComponentType.INTERFACES, interfaces.SPEC_BY_ID
)
BaseappMgrMsgSpecByID = ComponentMsgSpecById(
    ComponentType.BASEAPPMGR, baseappmgr.SPEC_BY_ID
)
CellappMgrMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CELLAPPMGR, cellappmgr.SPEC_BY_ID
)
BaseappMsgSpecByID = ComponentMsgSpecById(ComponentType.BASEAPP, baseapp.SPEC_BY_ID)
CellappMsgSpecByID = ComponentMsgSpecById(ComponentType.CELLAPP, cellapp.SPEC_BY_ID)
LoginappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.LOGINAPP, loginapp.SPEC_BY_ID
)
SupervisorMsgSpecByID = ComponentMsgSpecById(
    ComponentType.SUPERVISOR, supervisor.SPEC_BY_ID
)
