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

    kbe_loginapp_host = ""
    try:
        kbe_loginapp_host = env.str("KBE_LOGINAPP_HOST")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    kbe_loginapp_tcp_port = 0
    try:
        kbe_loginapp_tcp_port = env.int("KBE_LOGINAPP_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    kbe_client_entitydefs_digest = ""
    try:
        kbe_client_entitydefs_digest = env.str("KBE_CLIENT_ENTITYDEFS_DIGEST")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    loginapp_addr = Addr(
        get_real_host_ip(kbe_loginapp_host),
        Port(kbe_loginapp_tcp_port),
    )

    account_name = "".join(
        random.choice(string.ascii_letters) for _ in range(10)
    )
    password = "".join(random.choice(string.ascii_letters) for _ in range(10))

    logger.info("Connect to Loginapp (addr = '%s')", loginapp_addr)
    client = TcpMsgClient(loginapp_addr, ComponentType.CLIENT)
    res = await client.start()
    if not res.success:
        logger.error('Loginapp is not reachable (err = "%s")', res.text)
        sys.exit(1)

    cmd = LoginappLoginCommand(
        ClientType.LINUX,
        client_data=b"123",
        login_name=account_name,
        password=password,
        digest=kbe_client_entitydefs_digest,
        force_login=False,
        started_client=client,
    )
    res = await cmd.execute()
    if not res.success:
        logger.warning('Login is not success. Reason: "%s")', res.text)
        sys.exit(1)

    assert res.result is not None

    logger.info("Done (result = %s)", pprint.pformat(res.result))
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
