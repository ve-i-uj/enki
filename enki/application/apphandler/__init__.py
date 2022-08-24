from typing import Type

from enki import descr

from .base import IHandler, HandlerResult
from .entity import EntityHandler, OnCreatedProxiesHandler, OnEntityEnterSpaceHandler, OnSetEntityPosAndDirHandler, \
    OnUpdatePropertysHandler, OnRemoteMethodCallHandler, \
    OnEntityDestroyedHandler, OnEntityEnterWorldHandler, \
    OnUpdateBasePosHandler, OnUpdateBasePosXZHandler, OnUpdateData_XZ_Y_Handler
from .spacedata import SpaceDataHandler, InitSpaceDataHandler

E_HANDLER_CLS_BY_MSG_ID: dict[int, Type[EntityHandler]] = {
    descr.app.client.onUpdatePropertys.id: OnUpdatePropertysHandler,
    descr.app.client.onCreatedProxies.id: OnCreatedProxiesHandler,
    descr.app.client.onRemoteMethodCall.id: OnRemoteMethodCallHandler,
    descr.app.client.onEntityDestroyed.id: OnEntityDestroyedHandler,
    descr.app.client.onEntityEnterWorld.id: OnEntityEnterWorldHandler,
    descr.app.client.onSetEntityPosAndDir.id: OnSetEntityPosAndDirHandler,
    descr.app.client.onEntityEnterSpace.id: OnEntityEnterSpaceHandler,
    descr.app.client.onUpdateBasePos.id: OnUpdateBasePosHandler,
    descr.app.client.onUpdateBasePosXZ.id: OnUpdateBasePosXZHandler,
    descr.app.client.onUpdateData_xz_y.id: OnUpdateData_XZ_Y_Handler,
}

S_HANDLER_CLS_BY_MSG_ID: dict[int, Type[SpaceDataHandler]] = {
    descr.app.client.initSpaceData.id: InitSpaceDataHandler,
}
