"""Попробовать залогиниться на Loginapp и разорвать соединение.

Команда нужна для проверки, что логин работает.
"""

import asyncio
import logging
import pprint
import random
import string
import sys

from environs import Env, EnvError

from enki import settings
from enki.command.loginapp import LoginappLoginCommand
from enki.kbeenum import ClientType, ComponentType
from enki.misc import log
from enki.msg.msg_client import TcpMsgClient
from enki.net.addr import Addr, Port
from enki.net.server import get_real_host_ip

logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа."""
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    env = Env()
    got_error = False
    try:
        kbe_loginapp_host = env.str("KBE_LOGINAPP_HOST")
    except EnvError as err:
        got_error = True
        logger.warning(err)
    try:
        kbe_loginapp_tcp_port = env.int("KBE_LOGINAPP_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    loginapp_addr = Addr(
        get_real_host_ip(kbe_loginapp_host),  # pyright: ignore[reportPossiblyUnboundVariable]
        Port(kbe_loginapp_tcp_port),  # pyright: ignore[reportPossiblyUnboundVariable]
    )

    account_name = "".join(random.choice(string.ascii_letters) for _ in range(10))
    password = "".join(random.choice(string.ascii_letters) for _ in range(10))

    client = TcpMsgClient(loginapp_addr, ComponentType.CLIENT)
    res = await client.start()
    if not res.success:
        logger.error('Loginapp is not reachable (err = "%s")', res.text)
        sys.exit(1)

    cmd = LoginappLoginCommand(
        ClientType.LINUX,
        client_data=b"123",
        account_name=account_name,
        password=password,
        digest="sadfasf",
        force_login=False,
        started_client=client,
    )
    res = await cmd.execute()
    if not res.success:
        logger.error('No response (err="%s")', res.text)
        sys.exit(1)

    assert res.result is not None

    logger.info("Done (result = %s)", pprint.pformat(res.result))
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
