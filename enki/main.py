"""The entry point of the project."""

import asyncio
import datetime
import functools
import logging
import signal
import time

from tornado import ioloop

from enki.misc import log, devonly
from enki import connection, message, datahandler, serializer

from enki.msgspec.app import loginapp

logger = logging.getLogger(__name__)


def _sig_exit(shutdown_func, _signum, _frame):
    ioloop.IOLoop.current().add_callback_from_signal(shutdown_func)


def _shutdown(conn: connection.IConnection):
    logger.info('Stopping ioloop ...')
    io_loop = ioloop.IOLoop.current()
    conn.close()

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

    serializer_ = serializer.Serializer()
    msg_router = message.MessageRouter()
    incoming_handler = datahandler.IncomingDataHandler(msg_router, serializer_)

    login_app_conn = connection.LoginAppConnection(
        host='localhost',
        port=20013,
        serializer_=serializer_,
        handler=incoming_handler
    )

    shutdown_func = functools.partial(_shutdown, login_app_conn)
    sig_exit_func = functools.partial(_sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    await login_app_conn.connect()

    # TODO: [05.12.2020 16:53 a.burov@mednote.life]
    # Move from main
    hello_msg = message.Message(
        spec=loginapp.hello,
        fields=('2.5.10', '0.1.0', b'')
    )
    await login_app_conn.send(hello_msg)


if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
