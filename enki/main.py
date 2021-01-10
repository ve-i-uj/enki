"""The entry point of the project."""

import functools
import logging
import signal

from tornado import ioloop

from enki.misc import log
from enki import client
from enki import settings, runutil

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger('DEBUG')

    client_app = client.Client(loginapp_addr=settings.LOGIN_APP_ADDR)

    shutdown_func = functools.partial(runutil.shutdown, client_app)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    await client_app.start()

    await client_app.fire('login_loginapp', settings.ACCOUNT_NAME,
                          settings.PASSWORD)
    await client_app.fire('login_baseapp', settings.ACCOUNT_NAME,
                          settings.PASSWORD)

if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
