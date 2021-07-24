"""Plugin application."""

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

    app = appl.App(settings.LOGIN_APP_ADDR)
    await app.start(account_name, password)

    shutdown_func = functools.partial(runutil.shutdown, 0, app._client)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)


    # TODO: [29.03.2021 10:39 burov_alexey@mail.ru]
    # Это нужно, чтобы ловить все сообщения до закрытия соединения. Временно,
    # пока нет приёмника у приложения.
    import asyncio
    await asyncio.sleep(300)

    for _ in range(60):
        import asyncio
        await asyncio.sleep(10)

        cmd = command.baseapp.HelloCommand(
            kbe_version='2.5.10',
            script_version='0.1.0',
            encrypted_key=b'',
            client=baseapp_client
        )
        success, err_msg = await cmd.execute()
        if not success:
            logger.error(err_msg)
            return


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
    ioloop.IOLoop.current().start()
