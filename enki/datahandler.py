""""""

import abc

from enki import message
from enki import serializer


class IIncomingDataHandler(abc.ABC):
    
    @abc.abstractmethod
    def handle(self, data):
        pass


class IncomingDataHandler(IIncomingDataHandler):
    
    def __init__(self, msg_router: message.MessageRouter, 
                 serilazer_: serializer.Serializer):
        self._msg_router = msg_router
        self._serilazer = serilazer_ 

    def handle(self, data):
        msg = self._serilazer.deserialize(data)
        self._msg_router.on_receive_message(msg)
