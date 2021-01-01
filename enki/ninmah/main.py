"""Updater of client messages."""

import functools
import logging
import signal

from tornado import ioloop

from enki.misc import log
from enki import settings, runutil

from enki.ninmah import client, molder

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger('DEBUG')

    client_ = client.UpdaterClient(loginapp_addr=settings.LOGIN_APP_ADDR)

    shutdown_func = functools.partial(runutil.shutdown, client_)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    client_molder = molder.ClientMolder(
        client_=client_,
        account_name=settings.ACCOUNT_NAME,
        password=settings.PASSWORD,
        dst_path=settings.CODE_GEN_DST
    )
    await client_molder.mold()

    runutil.shutdown(client_)


if __name__ == '__main__':
    ioloop.IOLoop.current().asyncio_loop.create_task(main())
    ioloop.IOLoop.current().start()
