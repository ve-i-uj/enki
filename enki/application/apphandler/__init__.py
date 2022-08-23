from typing import Type

from enki import descr

from .base import HandlerResult, IHandler
from .entity import OnCreatedProxiesHandler, OnUpdatePropertysHandler, \
    OnRemoteMethodCallHandler, OnEntityDestroyedHandler, OnEntityEnterWorldHandler

HANDLER_CLS_BY_MSG_ID: dict[int, Type[IHandler]] = {
    descr.app.client.onUpdatePropertys.id: OnUpdatePropertysHandler,
    descr.app.client.onCreatedProxies.id: OnCreatedProxiesHandler,
    descr.app.client.onRemoteMethodCall.id: OnRemoteMethodCallHandler,
    descr.app.client.onEntityDestroyed.id: OnEntityDestroyedHandler,
    descr.app.client.onEntityEnterWorld.id: OnEntityEnterWorldHandler,
}

__all__ = [
    'HANDLER_CLS_BY_MSG_ID',
    'HandlerResult',
    'IHandler',
]
