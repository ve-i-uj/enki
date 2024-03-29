"""The external interface of the package."""

import asyncio
import logging
import queue
import threading
from typing import Type

from enki import settings
from enki.misc import devonly, log

from enki.core.enkitype import NoValue, AppAddr
from enki.core.gedescr import EntityDesc
from enki.core.msgspec import default_kbenginexml

from .layer import ilayer
from .layer.thlayer import ThreadedGameLayer, ThreadedNetLayer
from .gameentity import GameEntity
from .appl import App
from .eserializer import IEntityRPCSerializer
from .KBEngine import KBEngine

__all__ = [
    'start', 'stop', 'is_connected', 'sync_layers',
    'KBEngine',
]

logger = logging.getLogger(__name__)

_app: App
_loop: asyncio.AbstractEventLoop
_th_game_layer: ThreadedGameLayer
_th_net_layer: ThreadedNetLayer


def start(login_app_addr: AppAddr,
          entity_descriptions: dict[int, EntityDesc],
          entity_serializers: dict[str, Type[IEntityRPCSerializer]],
          kbenginexml_root: default_kbenginexml.root,
          game_entities: dict[str, Type[GameEntity]],
          server_tick_period: float = settings.SERVER_TICK_PERIOD
          ):
    """Start a network thread with the application and connect it to the game thread."""
    logger.info('[enki] Spawning Enki in the net thread')
    entity_serializer_by_uid = {
        cls.ENTITY_CLS_ID: cls for cls in entity_serializers.values()
    }
    app = App(login_app_addr, entity_descriptions, entity_serializer_by_uid,
              kbenginexml_root, server_tick_period)

    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()

    qame_queue = queue.Queue()

    net_layer = ThreadedNetLayer(entity_serializers, app, loop, qame_queue)
    game_layer = ThreadedGameLayer(game_entities, qame_queue)

    ilayer.init(net_layer, game_layer)

    global _app, _loop, _th_net_layer, _th_game_layer
    _app = app
    _loop = loop
    _th_net_layer = net_layer
    _th_game_layer = game_layer

    logger.info('[enki] Enki spawned')


def stop():
    """Schedules to stop app and io loop (the network thread will end after that)."""
    logger.info('[enki] Planning to stop the net thread')
    if _loop.is_running:
        asyncio.run_coroutine_threadsafe(_app.stop(), _loop)
        _loop.call_soon_threadsafe(_loop.stop)


def sync_layers(time_frame: float = settings.GAME_TICK):
    """Synchronizes the network and game layers, returns the number of calls received.

    While this function is running, client game entities will be updated
    in the calling thread.
    """
    count = _th_game_layer.sync_layers(time_frame)
    if count > 0:
        logger.debug('[enki] Received callbacks count: %s', count)
    return _th_game_layer.sync_layers(time_frame)


def is_connected() -> bool:
    try:
        return _app.is_connected
    except NameError:
        # Before spawning the network layer is called
        return False
