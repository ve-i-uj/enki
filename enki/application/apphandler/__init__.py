from typing import Type

from enki import descr

from .base import IHandler, HandlerResult
from .entity import EntityHandler, OnCreatedProxiesHandler, OnSetEntityPosAndDirHandler, \
    OnUpdatePropertysHandler, OnRemoteMethodCallHandler, \
    OnEntityDestroyedHandler, OnEntityEnterWorldHandler
from .spacedata import SpaceDataHandler, InitSpaceDataHandler

E_HANDLER_CLS_BY_MSG_ID: dict[int, Type[EntityHandler]] = {
    descr.app.client.onUpdatePropertys.id: OnUpdatePropertysHandler,
    descr.app.client.onCreatedProxies.id: OnCreatedProxiesHandler,
    descr.app.client.onRemoteMethodCall.id: OnRemoteMethodCallHandler,
    descr.app.client.onEntityDestroyed.id: OnEntityDestroyedHandler,
    descr.app.client.onEntityEnterWorld.id: OnEntityEnterWorldHandler,
    descr.app.client.onSetEntityPosAndDir.id: OnSetEntityPosAndDirHandler,
}

S_HANDLER_CLS_BY_MSG_ID: dict[int, Type[SpaceDataHandler]] = {
    descr.app.client.initSpaceData.id: InitSpaceDataHandler,
}
