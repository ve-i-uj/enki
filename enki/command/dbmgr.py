"""Commands for sending messages to the Logger component."""

import logging

from enki.core import msgspec
from enki.net.client import StreamClient

from ._base import LookAppCommand

logger = logging.getLogger(__name__)


class DBMgrLookAppCommand(LookAppCommand):
    """DBMgr command 'lookApp'."""

    def __init__(self, client: StreamClient):
        super().__init__(client, msgspec.app.dbmgr.lookApp,
                         msgspec.app.dbmgr.fakeRespLookApp)
