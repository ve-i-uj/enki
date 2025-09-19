"""The module contains procedures to request data for code generation."""

import logging

from enki import command, msgspec
from enki.net.addr import Addr


class StopClientException(Exception):
    """Signal to stop the client."""


logger = logging.getLogger(__name__)


async def entity_get_data(account_name: str, password: str) -> memoryview:
    """Request data of entity methods, property etc."""
    client = MsgTCPClient(LOGINAPP_ADDR, msgspec.client.SPEC_BY_ID)
    res = await client.start()
    if not res.success:
        logger.error(f"It cannot connect to the server (reason: {res.text})")
        raise StopClientException

    cmd = command.loginapp.LoginCommand(
        client_type=kbeenum.ClientType.UNKNOWN,
        client_data=b"",
        account_name=account_name,
        password=password,
        force_login=False,
        client=client,
    )
    client.set_msg_receiver(cmd)
    login_result = await cmd.execute()
    if not login_result.success:
        logger.error(
            f'Cannot connect to the "{LOGINAPP_ADDR}" server address '
            f'(err="{login_result.text}")'
        )
        raise StopClientException

    client.stop()

    baseapp_addr = Addr(
        ip_addr=login_result.result.host, port=login_result.result.tcp_port
    )
    client = MsgTCPClient(baseapp_addr, msgspec.client.SPEC_BY_ID)
    res = await client.start()
    if not res.success:
        logger.error(f"It cannot connect to the server (reason: {res.text})")
        raise StopClientException

    cmd = command.baseapp.ImportClientEntityDefCommand(client)
    client.set_msg_receiver(cmd)
    data = await cmd.execute()

    client.stop()

    return data
