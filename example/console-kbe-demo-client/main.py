#!/usr/bin/env python

"""Plugin application."""

import asyncio
import functools
import logging
import os
import signal
import random

from tornado import ioloop

from enki.app import App
from enki.misc import log, runutil
from enki import settings

# The generated code based on the server assets.
import descr
# The user implementation of the server entities.
import entities

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger(os.environ.get('LOG_LEVEL', 'DEBUG'))

    async def shutdown_func():
        logger.info('Interapting signal has been received ...')
        await runutil.shutdown(0)

    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    app = App(
        settings.AppAddr('localhost', 20013),
        settings.SERVER_TICK_PERIOD,
        entity_desc_by_uid=descr.entity.DESC_BY_UID,
        entity_impl_by_uid=entities.ENTITY_BY_UID,
        kbenginexml=descr.kbenginexml.root()
    )
    res = await app.start(
        account_name='1',
        password='1'
    )
    if not res.success:
        logger.error(res.text)
        app.on_end_receive_msg()
        return

    await asyncio.sleep(3)
    acc: entities.Account = list(app._entity_mgr._entities.values())[0]  # type: ignore
    acc.base.reqAvatarList()
    await asyncio.sleep(1)
    if not acc._avatars:
        acc.base.reqCreateAvatar(1, 'User name')
        await asyncio.sleep(2)
        acc.base.reqAvatarList()
        await asyncio.sleep(1)

    acc.base.selectAvatarGame(list(acc._avatars.keys())[0])


if __name__ == '__main__':
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
