"""Message sender / receiver of the application."""

import logging
from typing import Dict

from enki import descr, kbeclient
from damkina import apphandler, entitymgr

logger = logging.getLogger(__name__)


class MsgReceiver(kbeclient.IMsgReceiver):

    def __init__(self, entity_mgr: entitymgr.EntityMgr):
        self._handlers: Dict[int, apphandler.IHandler] = {
            descr.app.client.onUpdatePropertys.id: apphandler.OnUpdatePropertysHandler(entity_mgr),
            descr.app.client.onCreatedProxies.id: apphandler.OnCreatedProxiesHandler(entity_mgr),
        }

    def on_receive_msg(self, msg: kbeclient.Message) -> bool:
        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(f'[{self}] There is NO handler for the message '
                           f'"{msg.name}"')
            return False

        result: apphandler.HandlerResult = handler.handle(msg)

        return True
