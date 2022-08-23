"""This module contains procedures to request data for code generation."""

import logging
from typing import Tuple

from enki import settings, command, kbeenum, kbeclient, exception

logger = logging.getLogger(__name__)


async def app_get_data(account_name: str, password: str) -> Tuple[bytes, bytes]:
    """Request LoginApp, BaseApp, ClientApp messages."""
    # Request loginapp messages
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    cmd = command.loginapp.ImportClientMessagesCommand(client)
    await client.start()
    login_app_data = await cmd.execute()

    # Request baseapp messages
    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    login_result = await cmd.execute()
    if login_result.ret_code != kbeenum.ServerError.SUCCESS:
        logger.warning(f'It CANNOT connect to the server '
                       f'(reason: {login_result.ret_code})')
        raise exception.StopClientException(login_result.ret_code)

    await client.stop()

    baseapp_addr = settings.AppAddr(host=login_result.host,
                                    port=login_result.tcp_port)
    client = kbeclient.Client(baseapp_addr)
    await client.start()

    cmd = command.baseapp.ImportClientMessagesCommand(client)
    base_app_data = await cmd.execute()

    await client.stop()

    return login_app_data, base_app_data


async def entity_get_data(account_name: str, password: str) -> bytes:
    """Request data of entity methods, property etc."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    await client.start()
    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    login_result = await cmd.execute()

    await client.stop()

    baseapp_addr = settings.AppAddr(host=login_result.host,
                                    port=login_result.tcp_port)
    client = kbeclient.Client(baseapp_addr)
    await client.start()

    cmd = command.baseapp.ImportClientEntityDefCommand(client)
    data = await cmd.execute()

    await client.stop()

    return data


async def error_get_data() -> bytes:
    """Request error messages."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    cmd = command.loginapp.ImportServerErrorsDescrCommand(client)
    await client.start()
    error_data = await cmd.execute()

    await client.stop()

    return error_data
