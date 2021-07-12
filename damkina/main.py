"""Plugin application."""

import functools
import logging
import signal

from tornado import ioloop

from enki.misc import log, runutil
from enki import settings, command, kbeenum, kbeclient, descr

from damkina import receiver

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger('DEBUG')

    account_name = settings.ACCOUNT_NAME
    password = settings.PASSWORD

    client = kbeclient.Client(settings.LOGIN_APP_ADDR)

    shutdown_func = functools.partial(runutil.shutdown, 0, client)
    sig_exit_func = functools.partial(runutil.sig_exit, shutdown_func)
    signal.signal(signal.SIGINT, sig_exit_func)
    signal.signal(signal.SIGTERM, sig_exit_func)

    await client.start()

    cmd = command.loginapp.HelloCommand(
        kbe_version='2.5.10',
        script_version='0.1.0',
        encrypted_key=b'',
        client=client
    )
    success, err_msg = await cmd.execute()
    if not success:
        logger.error(err_msg)
        return

    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    login_result: command.loginapp.LoginCommandResult = await cmd.execute()

    if login_result.ret_code != kbeenum.ServerError.SUCCESS:
        err_msg = login_result.data.decode()
        logger.warning(f'The client cannot connect to LoginApp '
                       f'(code = {login_result.ret_code}, msg = {err_msg})')
        return

    # We got the BaseApp address and do not need the LoginApp connection anymore
    await client.stop()

    baseapp_addr = settings.AppAddr(host=login_result.host,
                                    port=login_result.tcp_port)
    baseapp_client = kbeclient.Client(baseapp_addr)
    await baseapp_client.start()

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

    # This message starts the client-server communication. The server will send
    # many initial messages in the response. But it can return nothing
    # (no server response and stop waiting by timeout)
    baseapp_client.set_msg_receiver(receiver.MsgReceiver())
    msg = kbeclient.Message(descr.app.baseapp.loginBaseapp, (account_name, password))
    await baseapp_client.send(msg)

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
