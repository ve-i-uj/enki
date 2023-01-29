"""Commands for sending messages to the Logger component."""

import logging

from enki.net import msgspec
from enki.net.kbeclient.client import StreamClient

from ._base import LookAppCommand

logger = logging.getLogger(__name__)


class InterfacesLookAppCommand(LookAppCommand):
    """Logger command 'lookApp'."""

    def __init__(self, client: StreamClient):
        # Передаём в конструктор родителя, что будем запрашивать и как
        # будем обрабатывать ответ.
        super().__init__(client, msgspec.app.interfaces.lookApp,
                         msgspec.app.interfaces.fakeRespLookApp)
