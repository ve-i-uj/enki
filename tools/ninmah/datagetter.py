"""This module contains procedures to request data for code generation."""

import logging
from typing import Tuple

from enki import command, kbeenum, kbeclient, exception, interface
from tools.ninmah import settings

logger = logging.getLogger(__name__)


async def app_get_data(account_name: str, password: str) -> Tuple[bytes, bytes]:
    """Request LoginApp, BaseApp, ClientApp messages."""
    # Request loginapp messages
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    cmd_5 = command.loginapp.ImportClientMessagesCommand(client)
    res: interface.IResult = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{settings.LOGIN_APP_ADDR}" server address '
                     f'(err="{res.text}")')
        raise exception.StopClientException

    client.set_msg_receiver(cmd_5)
    resp_5 = await cmd_5.execute()
    if not resp_5.success:
        raise exception.StopClientException(resp_5.text)

    # Request baseapp messages
    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    client.set_msg_receiver(cmd)
    login_res = await cmd.execute()
    if not login_res.success:
        logger.warning(f'It cannot connect to the server '
                       f'(reason: {login_res.text})')
        raise exception.StopClientException()

    await client.stop()

    baseapp_addr = interface.AppAddr(host=login_res.result.host,
                                    port=login_res.result.tcp_port)
    client = kbeclient.Client(baseapp_addr)
    await client.start()

    cmd_207 = command.baseapp.ImportClientMessagesCommand(client)
    client.set_msg_receiver(cmd_207)
    resp_207 = await cmd_207.execute()
    if not resp_207.success:
        raise exception.StopClientException(resp_207.text)

    await client.stop()

    return resp_5.result.data, resp_207.result.data


async def entity_get_data(account_name: str, password: str) -> memoryview:
    """Request data of entity methods, property etc."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    await client.start()
    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    client.set_msg_receiver(cmd)
    login_result = await cmd.execute()

    await client.stop()

    baseapp_addr = interface.AppAddr(host=login_result.result.host,
                                    port=login_result.result.tcp_port)
    client = kbeclient.Client(baseapp_addr)
    await client.start()

    cmd = command.baseapp.ImportClientEntityDefCommand(client)
    client.set_msg_receiver(cmd)
    data = await cmd.execute()

    await client.stop()

    return data


async def error_get_data() -> memoryview:
    """Request error messages."""
    client = kbeclient.Client(settings.LOGIN_APP_ADDR)
    cmd = command.loginapp.ImportServerErrorsDescrCommand(client)
    client.set_msg_receiver(cmd)
    await client.start()
    error_data = await cmd.execute()

    await client.stop()

    return error_data
