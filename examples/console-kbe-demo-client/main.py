import logging
import sys
import time

# Generated code for the concrete assets version (entity methods, properties and types)
import descr

# Implementation of the entity methods for the concrete assets version
import entities
import environs

from enki import settings
from enki.app import client
from enki.apps.clientapp import KBEngine

from enki.misc import log
from enki.net.addr import Addr

logger = logging.getLogger(__name__)

_env = environs.Env()
GAME_ACCOUNT_NAME: str = _env.str("GAME_ACCOUNT_NAME")
GAME_PASSWORD: str = _env.str("GAME_PASSWORD")


def main():
    # Set logging level
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    # Run network logic in a separate thread
    client.start(
        Addr("localhost", 20013),
        descr.description.DESC_BY_UID,
        descr.eserializer.SERIAZER_BY_ECLS_NAME,
        descr.kbenginexml.root(),
        entities.ENTITY_CLS_BY_NAME,
    )

    # Login using KBEngine API
    KBEngine.login(GAME_ACCOUNT_NAME, GAME_PASSWORD)
    # This thread is waiting for connection result, so it doesn't need GIL
    stop_time = (
        time.time() + settings.CONNECT_TO_SERVER_TIMEOUT + settings.SECOND * 5
    )
    while not client.is_connected() and stop_time > time.time():
        logger.debug(
            f"Waiting for server connection "
            f"or exit by timeout (exit time = {stop_time}, now = {time.time()})"
        )
        client.sync_layers(settings.SECOND * 3)

    if not client.is_connected():
        logger.error("Cannot connect to the server. See log records")
        sys.exit(1)

    logger.info("The client net component is ready")

    from entities.account import Account

    acc: Account = KBEngine.player()  # type: ignore
    if acc is None:
        logger.error("Something is going wrong. There is no Account entity")
        sys.exit(1)

    acc.base.reqAvatarList()
    client.sync_layers(settings.SECOND * 0.5)

    if acc.current_avatar_dbid == NoValue.NO_ID:
        acc.base.reqCreateAvatar(1, f"enki_bot_{acc.id}")
        client.sync_layers(settings.SECOND * 0.5)

    if acc.current_avatar_dbid == NoValue.NO_ID:
        logger.error("Something is going wrong. See server log records")
        sys.exit(1)

    acc.base.selectAvatarGame(acc.current_avatar_dbid)

    try:
        while True:
            client.sync_layers()
    except KeyboardInterrupt:
        client.stop()
    logger.info("Done")


if __name__ == "__main__":
    main()
