""""""

import abc

from enki import message
from enki import serializer


class IIncomingDataHandler(abc.ABC):
    """Interface for handling of incoming server messages."""
    
    @abc.abstractmethod
    def handle(self, data):
        """Handle incoming data from a server."""
        pass


class IncomingDataHandler(IIncomingDataHandler):
    
    def __init__(self, msg_router: message.MessageRouter,
                 serializer_: serializer.Serializer):
        self._msg_router = msg_router
        self._serializer = serializer_

    def handle(self, data):
        msg = self._serializer.deserialize(data)
        self._msg_router.on_receive_message(msg)
