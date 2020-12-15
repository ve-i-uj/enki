"""Updater client."""

import logging

from enki import client
from enki import settings

from . import protocol

logger = logging.getLogger(__name__)


class UpdaterClient(client.Client):
    """Client to get last message specification."""

    _PROTOCOLS = {
        settings.ComponentEnum.LOGINAPP: protocol.LoginAppUpdaterProtocol,
        settings.ComponentEnum.BASEAPP: protocol.BaseAppUpdaterProtocol,
    }
