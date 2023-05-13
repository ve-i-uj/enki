"""This module contains procedures to request data for code generation."""

import logging
from typing import Tuple

from enki.core import kbeenum
from enki import command
from enki.core import msgspec
from enki.core.enkitype import Result, AppAddr
from enki.net.client import TCPClient

from tools.ninmah import settings


class StopClientException(Exception):
    """Signal to stop the client."""
    pass


logger = logging.getLogger(__name__)


async def app_get_data(account_name: str, password: str) -> tuple[memoryview, memoryview]:
    """Request LoginApp, BaseApp, ClientApp messages."""
    # Request loginapp messages
    client = TCPClient(settings.LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
    cmd_5 = command.loginapp.ImportClientMessagesCommand(client)
    res: Result = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{settings.LOGIN_APP_ADDR}" server address '
                     f'(err="{res.text}")')
        raise StopClientException

    client.set_msg_receiver(cmd_5)
    resp_5 = await cmd_5.execute()
    if not resp_5.success:
        raise StopClientException(resp_5.text)

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
        raise StopClientException()

    client.stop()

    baseapp_addr = AppAddr(host=login_res.result.host,
                                    port=login_res.result.tcp_port)
    client = TCPClient(baseapp_addr, msgspec.app.client.SPEC_BY_ID)
    await client.start()

    cmd_207 = command.baseapp.ImportClientMessagesCommand(client)
    client.set_msg_receiver(cmd_207)
    resp_207 = await cmd_207.execute()
    if not resp_207.success:
        raise StopClientException(resp_207.text)

    client.stop()

    return resp_5.result.data, resp_207.result.data


async def entity_get_data(account_name: str, password: str) -> memoryview:
    """Request data of entity methods, property etc."""
    client = TCPClient(settings.LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
    res = await client.start()
    if not res.success:
        logger.error(f'It cannot connect to the server (reason: {res.text})')
        raise StopClientException()

    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN, client_data=b'',
        account_name=account_name, password=password, force_login=False,
        client=client
    )
    client.set_msg_receiver(cmd)
    login_result = await cmd.execute()
    if not login_result.success:
        logger.error(f'Cannot connect to the "{settings.LOGIN_APP_ADDR}" server address '
                     f'(err="{login_result.text}")')
        raise StopClientException

    client.stop()

    baseapp_addr = AppAddr(host=login_result.result.host,
                                    port=login_result.result.tcp_port)
    client = TCPClient(baseapp_addr, msgspec.app.client.SPEC_BY_ID)
    res = await client.start()
    if not res.success:
        logger.error(f'It cannot connect to the server (reason: {res.text})')
        raise StopClientException()

    cmd = command.baseapp.ImportClientEntityDefCommand(client)
    client.set_msg_receiver(cmd)
    data = await cmd.execute()

    client.stop()

    return data


async def error_get_data() -> memoryview:
    """Request error messages."""
    client = TCPClient(settings.LOGIN_APP_ADDR, msgspec.app.client.SPEC_BY_ID)
    cmd = command.loginapp.ImportServerErrorsDescrCommand(client)
    client.set_msg_receiver(cmd)
    await client.start()
    error_data = await cmd.execute()

    client.stop()

    return error_data
