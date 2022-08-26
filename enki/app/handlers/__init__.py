from typing import Type

from enki import descr

from .base import IHandler, HandlerResult
from .ehandler import *
from .sdhandler import *

E_HANDLER_CLS_BY_MSG_ID: dict[int, Type[EntityHandler]] = {
    descr.app.client.onUpdatePropertys.id: OnUpdatePropertysHandler,
    descr.app.client.onUpdatePropertysOptimized.id: OnUpdatePropertysOptimizedHandler,
    descr.app.client.onCreatedProxies.id: OnCreatedProxiesHandler,
    descr.app.client.onRemoteMethodCall.id: OnRemoteMethodCallHandler,
    descr.app.client.onEntityDestroyed.id: OnEntityDestroyedHandler,
    descr.app.client.onEntityEnterWorld.id: OnEntityEnterWorldHandler,
    descr.app.client.onSetEntityPosAndDir.id: OnSetEntityPosAndDirHandler,
    descr.app.client.onEntityEnterSpace.id: OnEntityEnterSpaceHandler,
    descr.app.client.onUpdateBasePos.id: OnUpdateBasePosHandler,
    descr.app.client.onUpdateBasePosXZ.id: OnUpdateBasePosXZHandler,
    descr.app.client.onUpdateData_xz_y.id: OnUpdateData_XZ_Y_Handler,
    descr.app.client.onUpdateData_xz.id: OnUpdateData_XZ_Handler,
}

S_HANDLER_CLS_BY_MSG_ID: dict[int, Type[SpaceDataHandler]] = {
    descr.app.client.initSpaceData.id: InitSpaceDataHandler,
}
