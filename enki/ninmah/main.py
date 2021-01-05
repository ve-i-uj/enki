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

    client_ = client.NinmahClient(loginapp_addr=settings.LOGIN_APP_ADDR)

    shutdown_func = functools.partial(runutil.shutdown, client_)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    # await client_.start()
    # client_molder = molder.ClientMolder(
    #     client_=client_,
    #     account_name=settings.ACCOUNT_NAME,
    #     password=settings.PASSWORD,
    #     dst_path=settings.CodeGenDstPath.APP
    # )
    # await client_molder.mold()
    # client_.stop()

    await client_.start()
    entity_molder = molder.EntityMolder(
        client_=client_,
        account_name=settings.ACCOUNT_NAME,
        password=settings.PASSWORD,
        dst_path=settings.CodeGenDstPath.TYPE
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
