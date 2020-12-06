"""The entry point of the project."""

import asyncio
import functools
import logging
import signal
import time

from tornado import ioloop

from enki.misc import log
from enki import client
from enki import settings

logger = logging.getLogger(__name__)


def _sig_exit(shutdown_func, _signum, _frame):
    ioloop.IOLoop.current().add_callback_from_signal(shutdown_func)


def _shutdown(conn: client.Client):
    logger.info('Stopping ioloop ...')
    io_loop = ioloop.IOLoop.current()
    conn.stop()

    deadline = time.time() + 2

    def stop_loop():
        now = time.time()
        if now < deadline and asyncio.all_tasks():
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logger.info('Shutdown completed')

    stop_loop()


async def main():
    log.setup_root_logger('DEBUG')

    client_app = client.Client(loginapp_addr=settings.LOGIN_APP_ADDR)

    shutdown_func = functools.partial(_shutdown, client_app)
    sig_exit_func = functools.partial(_sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    await client_app.start()

    await client_app.fire('login', '1', '1')

if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
