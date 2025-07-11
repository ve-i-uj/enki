"""Описания KBEngine-сообщений."""

from enki.kbeenum import ComponentType
from enki.msg.msg_descr import ComponentMsgSpecById

from . import (
    baseapp,
    baseappmgr,
    cellapp,
    cellappmgr,
    clientapp,
    dbmgr,
    interfaces,
    logger,
    loginapp,
    machine,
    supervisor,
)

ClienappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CLIENT, clientapp.SPEC_BY_ID
)
MachineMsgSpecByID = ComponentMsgSpecById(
    ComponentType.MACHINE, machine.SPEC_BY_ID
)
LoggerMsgSpecByID = ComponentMsgSpecById(
    ComponentType.LOGGER, logger.SPEC_BY_ID)
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
BaseappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.BASEAPP, baseapp.SPEC_BY_ID)
CellappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.CELLAPP, cellapp.SPEC_BY_ID)
LoginappMsgSpecByID = ComponentMsgSpecById(
    ComponentType.LOGINAPP, loginapp.SPEC_BY_ID
)

SupervisorMsgSpecByID = ComponentMsgSpecById(
    ComponentType.SUPERVISOR, supervisor.SPEC_BY_ID)

# TODO: [burov_alexey@mail.ru 10.07.2025 14:15]
# Удалить

# Добим пользовательское сообщение во все компоненты от которых оно будет ожидаться.
# app.machine.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.logger.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.interfaces.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.dbmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.cellappmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.baseappmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.baseapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.cellapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
# app.loginapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp

# app.machine.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.logger.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.interfaces.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.dbmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.cellappmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.baseappmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.baseapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.cellapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
# app.loginapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
