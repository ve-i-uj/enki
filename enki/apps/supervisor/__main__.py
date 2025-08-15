"""Входная точка для запуска приложения-компонента Supervisor."""

import asyncio
import contextlib
import logging
import sys

from environs import Env, EnvError

from enki import settings
from enki.apps.supervisor.supervisor_app import Supervisor
from enki.misc import log
from enki.net.addr import Addr, Port

logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа."""
    # Формат нужно задать такой же, как и остальных компонентов, чтобы LogStash
    # мог понимать эти логи. Формат KBE логов:
    # INFO component_name [2023-01-01 00:00:01,000] - Whatever
    log_format = "%(levelname)s supervisor [%(asctime)s] - [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"  # noqa: E501
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL), log_format)

    env = Env()
    got_error = False

    try:
        kbe_machine_host = env.str("KBE_MACHINE_HOST")
    except EnvError as err:
        got_error = True
        logger.error(err)
    try:
        kbe_machine_tcp_port = env.int("KBE_MACHINE_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.error(err)
    try:
        kbe_machine_udp_port = env.int("KBE_MACHINE_UDP_PORT")
    except EnvError as err:
        got_error = True
        logger.error(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    app = Supervisor(
        udp_addr=Addr(kbe_machine_host, Port(kbe_machine_udp_port)),
        tcp_addr=Addr(kbe_machine_host, Port(kbe_machine_tcp_port)),
    )

    try:
        res = await app.start()
        if not res.success:
            logger.error("UDP server cannot start. Error %s", res.text)
            sys.exit(1)

        await app.wait_until_stop()
        logger.info("Supervisor stopped")
    except Exception as err:
        logger.error(err, exc_info=True)
        app.stop()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
