#!/usr/bin/env python

"""Plugin application."""

import asyncio
import functools
import logging
import os
import signal

from tornado import ioloop

from enki.misc import log, runutil
from enki import settings

from enki.application import appl
from enki.application import entities

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger(os.environ.get('LOG_LEVEL', 'DEBUG') or 'DEBUG')

    async def shutdown_func():
        logger.info('Interapting signal has been received ...')
        await runutil.shutdown(0)

    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    app = appl.App(settings.LOGIN_APP_ADDR, settings.SERVER_TICK_PERIOD)
    success, err_msg = await app.start(settings.ACCOUNT_NAME, settings.PASSWORD)
    if not success:
        logger.error(f'{err_msg}. Exit')
        return

    await asyncio.sleep(3)
    acc: entities.Account = list(app._entity_mgr._entities.values())[0]  # type: ignore
    acc.base.reqAvatarList()
    await asyncio.sleep(1)
    if not acc._avatars:
        acc.base.reqCreateAvatar(1, 'Damkina')
        await asyncio.sleep(1)
    acc.base.selectAvatarGame(list(acc._avatars.keys())[0])

    # acc.base.req_get_avatars(1)
    # await asyncio.sleep(10)


if __name__ == '__main__':
    # TODO: [04.03.2021 20:32 burov_alexey@mail.ru]
    # На время отладки, чтобы сразу ошибку ловить
    async def _main():
        try:
            await main()
        except SystemExit:
            await runutil.shutdown(0)
        except Exception as err:
            logger.error(err, exc_info=True)
            await runutil.shutdown(0)

    ioloop.IOLoop.current().asyncio_loop.create_task(_main())  # type: ignore
    ioloop.IOLoop.current().start()
