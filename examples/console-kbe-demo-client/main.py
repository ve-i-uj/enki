import asyncio
import logging
import sys
import time

import enki
from enki import KBEngine

from enki import settings
from enki.enkitype import AppAddr
from enki.net.kbeclient import Client
from enki.net.command.loginapp import HelloCommand
from enki.misc import log

# Generated code for the concrete assets version (entity methods, properties and types)
import descr
# Implementation of the entity methods for the concrete assets version
import entities

logger = logging.getLogger(__name__)


def main():
    # Выставить уровень логирования
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    # Запустить сетевую логику в отдельном трэде
    enki.spawn(
        AppAddr('localhost', 20013),
        descr.description.DESC_BY_UID,
        descr.eserializer.SERIAZER_BY_ECLS_NAME,
        descr.kbenginexml.root(),
        entities.ENTITY_CLS_BY_NAME
    )

    # Логин средствами API KBEngine.
    KBEngine.login(settings.GAME_ACCOUNT_NAME, settings.GAME_PASSWORD)
    # Этот трэд ждёт результата подключения, поэтому ему GIL не нужен.
    stop_time = time.time() + settings.CONNECT_TO_SERVER_TIMEOUT + settings.SECOND * 5
    while not enki.is_connected() and stop_time > time.time():
        logger.debug(f'Waiting for server connection '
                     f'or exit by timeout (exit time = {stop_time}, now = {time.time()})')
        enki.sync_layers(settings.SECOND * 3)

    if not enki.is_connected():
        logger.error('Cannot connect to the server. See log records')
        sys.exit(1)

    logger.info('The client net component is ready')

    from entities.account import Account
    acc: Account = KBEngine.player() # type: ignore
    if acc is None:
        logger.error('Something is going wrong. There is no Account entity')
        sys.exit(1)

    acc.base.reqAvatarList()
    enki.sync_layers(settings.SECOND * 0.5)

    if acc.current_avatar_dbid == settings.NO_ID:
        acc.base.reqCreateAvatar(1, f'enki_bot_{acc.id}')
        enki.sync_layers(settings.SECOND * 0.5)

    if acc.current_avatar_dbid == settings.NO_ID:
        logger.error('Something is going wrong. See server log records')
        sys.exit(1)

    acc.base.selectAvatarGame(acc.current_avatar_dbid)

    try:
        while True:
            enki.sync_layers()
    except KeyboardInterrupt:
        enki.stop()
    logger.info(f'Done')

if __name__ == '__main__':
    main()
