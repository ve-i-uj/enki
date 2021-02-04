"""Utilites for running / stopping this service."""

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

_SHUTDOWN_TIMEOUT = 2


def sig_exit(shutdown_func, _signum, _frame):
    ioloop.IOLoop.current().add_callback_from_signal(shutdown_func)


def shutdown(client_: client.Client, timeout=_SHUTDOWN_TIMEOUT):
    logger.info('Stopping ioloop ...')
    io_loop = ioloop.IOLoop.current()
    client_.stop()

    deadline = time.time() + timeout

    def stop_loop():
        now = time.time()
        # Waiting for completion of scheduled tasks
        if now < deadline and asyncio.all_tasks():
            io_loop.add_timeout(now + 1, stop_loop)
        else:
            io_loop.stop()
            logger.info('Shutdown completed')

    stop_loop()
