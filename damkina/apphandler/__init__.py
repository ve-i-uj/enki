# TODO: [25.07.2021 burov_alexey@mail.ru]:
# Не понятно, что происходит с импортами
from .base import HandlerResult, IHandler
from .entity import OnCreatedProxiesHandler, OnUpdatePropertysHandler, \
    OnRemoteMethodCallHandler, OnEntityDestroyedHandler
