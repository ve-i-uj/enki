"""Message sender / receiver of the application."""

import logging
from typing import Dict

from enki import interface, descr

from damkina import apphandler

logger = logging.getLogger(__name__)


class MsgReceiver(interface.IMsgReceiver):

    def __init__(self):
        self._handlers: Dict[int, apphandler.IHandler] = {
            descr.app.client.onUpdatePropertys.id: apphandler.entity.OnUpdatePropertysHandler(),
        }

    def on_receive_msg(self, msg: interface.IMessage) -> bool:
        handler = self._handlers.get(msg.id)
        if handler is None:
            logger.warning(f'[{self}] There is NO handler for the message '
                           f'"{msg.name}"')
            return False

        result: apphandler.HandlerResult = handler.handle(msg)

        return True
