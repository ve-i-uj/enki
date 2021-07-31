"""Plugin application."""

import asyncio
import functools
import logging
import signal

from tornado import ioloop

from enki.misc import log, runutil
from enki import settings, command, kbeenum, kbeclient, descr

from damkina import appl

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger('DEBUG')

    account_name = settings.ACCOUNT_NAME
    password = settings.PASSWORD

    app = appl.App(settings.LOGIN_APP_ADDR, settings.SERVER_TICK_PERIOD)
    await app.start(account_name, password)

    shutdown_func = functools.partial(runutil.shutdown, 0, app._client)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)


if __name__ == '__main__':
    # TODO: [04.03.2021 20:32 burov_alexey@mail.ru]
    # На время отладки, чтобы сразу ошибку ловить
    async def _main():
        try:
            await main()
        except Exception as err:
            logger.error(err, exc_info=True)
        await runutil.shutdown(0)

    ioloop.IOLoop.current().asyncio_loop.create_task(_main())
    ioloop.IOLoop.current().asyncio_loop.run_forever()
    ioloop.IOLoop.current().start()
