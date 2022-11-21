import asyncio
import queue
import threading
from typing import Type

from .misc import devonly
from .KBEngine import KBEngine

from . import layer, settings
from .enkitype import AppAddr
from .gedescr import EntityDesc

from .net.netentity import IEntityRPCSerializer
from .net.msgspec import default_kbenginexml

from .app.appl import App
from .app.thlayer import ThreadedGameLayer, ThreadedNetLayer
from .app.gameentity import GameEntity


_app: App
_loop: asyncio.AbstractEventLoop
def spawn(login_app_addr: AppAddr,
          entity_descriptions: dict[int, EntityDesc],
          entity_serializers: dict[str, Type[IEntityRPCSerializer]],
          kbenginexml_root: default_kbenginexml.root,
          game_entities: dict[str, Type[GameEntity]],
          server_tick_period: float = settings.SERVER_TICK_PERIOD
          ):
    entity_serializer_by_uid = {
        cls.ENTITY_CLS_ID: cls for cls in entity_serializers.values()
    }
    app = App(login_app_addr, entity_descriptions, entity_serializer_by_uid,
                   kbenginexml_root, server_tick_period)

    loop = asyncio.get_event_loop()
    thread = threading.Thread(target=loop.run_forever)
    thread.start()

    qame_queue = queue.Queue()

    net_layer = ThreadedNetLayer(entity_serializers, app, loop, qame_queue)
    game_layer = ThreadedGameLayer(game_entities, qame_queue)

    layer.init(net_layer, game_layer)

    global _app, _loop
    _app = app
    _loop = loop


def stop():
    _loop.call_soon_threadsafe(_app.stop)
    _loop.call_soon_threadsafe(_loop.stop)
