from typing import Type

from enki.core import msgspec

from ..base import Handler, HandlerResult
from . import machinehandler, interfaceshandler, dbmgrhandler, loggerhandler, \
    cellappmgrhandler

# Handlers by the server component name
SERVER_HANDLERS: dict[str, dict[int, Type[Handler]]] = {
    'machine': {
        msgspec.app.machine.onBroadcastInterface.id: machinehandler.OnBroadcastInterfaceHandler,
        msgspec.app.machine.onFindInterfaceAddr.id: machinehandler.OnFindInterfaceAddrHandler,
        msgspec.app.machine.queryComponentID.id: machinehandler.QueryComponentIDHandler,
    },
    'interfaces': {
        msgspec.app.interfaces.onRegisterNewApp.id: interfaceshandler.OnRegisterNewAppHandler,
        msgspec.app.interfaces.onAppActiveTick.id: interfaceshandler.OnAppActiveTickHandler,
    },
    'dbmgr': {
        msgspec.app.dbmgr.onRegisterNewApp.id: dbmgrhandler.OnRegisterNewAppHandler,
        msgspec.app.dbmgr.onAppActiveTick.id: dbmgrhandler.OnAppActiveTickHandler,
    },
    'cellappmgr': {
        msgspec.app.cellappmgr.onAppActiveTick.id: cellappmgrhandler.OnAppActiveTickHandler,
    },
    'logger': {
        msgspec.app.logger.writeLog.id: loggerhandler.WriteLogHandler,
        msgspec.app.logger.onRegisterNewApp.id: loggerhandler.OnRegisterNewAppHandler,
    },
}
