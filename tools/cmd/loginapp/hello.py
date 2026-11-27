import asyncio
import logging
import sys

from environs import Env, EnvError

from enki import settings
from enki.apps.clientapp.clients.loginapp_client import (
    LoginappClient,
)
from enki.kbeenum import ComponentType
from enki.misc import log
from enki.net import server
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)


async def main() -> None:
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    env = Env()
    got_error = False

    kbe_loginapp_host = env.str("KBE_LOGINAPP_HOST", "")
    kbe_component_name = env.str("KBE_COMPONENT_NAME", "")

    loginapp_host = kbe_loginapp_host
    if loginapp_host == "":
        loginapp_host = kbe_component_name
    if loginapp_host == "":
        got_error = True
        logger.warning(
            "The Loginapp host is not set. Set remote host variable "
            '"KBE_LOGINAPP_HOST" or "KBE_COMPONENT_NAME" variable'
        )

    kbe_loginapp_tcp_port = 0
    try:
        kbe_loginapp_tcp_port = env.int("KBE_LOGINAPP_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    loginapp_addr = Addr(
        server.get_real_host_ip(kbe_loginapp_host),
        Port(kbe_loginapp_tcp_port),
    )

    host = server.get_real_host_ip(loginapp_addr.ip_addr)
    addr = Addr(host, loginapp_addr.port)
    loginapp_client = LoginappClient(
        addr,
        ComponentType.TOOL,
        wait_response_seconds=5 * settings.SECOND,
        server_tick_period=-1,
    )
    try:
        res = await loginapp_client.start()
        if not res.success:
            logger.error(
                'Cannot connect to the "%s" server address (err="%s")', addr, res.text
            )
            return

        res = await loginapp_client.hello(
            kbe_version="2.5.10",
            assets_version="0.1.0",
            encrypted_key=b"",
        )

        logger.info("Done (result = %s)", res)

    except Exception as err:
        logger.error('No response (err="%s")', err)
        logger.exception("")
    finally:
        loginapp_client.stop()


if __name__ == "__main__":
    asyncio.run(main())
