"""Packet gives specification classes of server communication."""

from . import app, default_kbenginexml
from . import custom

# Добим пользовательское сообщение во все компоненты от которых оно будет ожидаться.
app.machine.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.logger.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.interfaces.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.dbmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.cellappmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.baseappmgr.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.baseapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.cellapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp
app.loginapp.SPEC_BY_ID[custom.onLookApp.id] = custom.onLookApp

app.machine.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.logger.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.interfaces.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.dbmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.cellappmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.baseappmgr.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.baseapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.cellapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
app.loginapp.SPEC_BY_ID[custom.onReqCloseServer.id] = custom.onReqCloseServer
