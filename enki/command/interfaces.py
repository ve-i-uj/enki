"""Commands for sending messages to the Logger component."""

import logging

from enki.core import msgspec
from enki.net.client import StreamClient

from .common import LookAppCommand

logger = logging.getLogger(__name__)


class InterfacesLookAppCommand(LookAppCommand):
    """Logger command 'lookApp'."""

    def __init__(self, client: StreamClient):
        # Передаём в конструктор родителя, что будем запрашивать и как
        # будем обрабатывать ответ.
        super().__init__(client, msgspec.app.interfaces.lookApp,
                         msgspec.app.interfaces.fakeRespLookApp)
