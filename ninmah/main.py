"""Updater of client messages."""

import argparse
import functools
import logging
import signal

from tornado import ioloop

from enki.misc import log
from enki import settings, runutil

from ninmah import molder
from ninmah import client

logger = logging.getLogger(__name__)


def read_args():
    desc = 'Ninmah. Code generator for client-server communication messages.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--generate', dest='generate', type=str,
                        action='append', nargs='+',
                        choices=['app', 'entity', 'error'],
                        help='The namespace of messages that will be generated')
    parser.add_argument('--clean-up', dest='clean_up', action='store_true',
                        help='Clean up all generated modules')
    parser.add_argument('--send-message', dest='send_message_data', type=str,
                        help='Send the message to the server. Format: <MSG_NAME> '
                             '<ARG_1> <ARG_2> .. <ARG_N> (example: %s)'
                             '' % "Loginapp::hello '2.5.10', '0.1.0', b''")
    parser.add_argument('--log-level', dest='log_level', type=str,
                        help='Log level (default: %(default)s)', default='DEBUG')

    return parser.parse_args()


async def main():
    try:
        namespace = read_args()
    except SystemExit:
        # run with --help arguments
        runutil.shutdown(client.NinmahClient(None), timeout=0)
        return

    log.setup_root_logger(namespace.log_level)

    client_ = client.NinmahClient(loginapp_addr=settings.LOGIN_APP_ADDR)

    shutdown_func = functools.partial(runutil.shutdown, client_)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    await client_.start()
    client_molder = molder.ClientMolder(
        client_=client_,
        account_name=settings.ACCOUNT_NAME,
        password=settings.PASSWORD,
        dst_path=settings.CodeGenDstPath.APP
    )
    await client_molder.mold()
    client_.stop()

    await client_.start()
    entity_molder = molder.EntityMolder(
        client_=client_,
        account_name=settings.ACCOUNT_NAME,
        password=settings.PASSWORD,
        type_dst_path=settings.CodeGenDstPath.TYPE,
        entity_dst_path=settings.CodeGenDstPath.ENTITY
    )
    await entity_molder.mold()
    client_.stop()

    await client_.start()
    entity_molder = molder.ServerErrorMolder(
        client_=client_,
        dst_path=settings.CodeGenDstPath.SERVERERROR
    )
    await entity_molder.mold()
    client_.stop()

    runutil.shutdown(client_)


if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
