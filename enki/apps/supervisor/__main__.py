"""Входная точка для запуска приложения-компонента Supervisor."""

import asyncio
import logging
import sys

from enki.apps.supervisor import settings
from enki.apps.supervisor.supervisor_app import Supervisor
from enki.misc import log
from enki.net.addr import Addr

logger = logging.getLogger(__name__)

# Формат нужно задать такой же, как и остальных компонентов, чтобы LogStash
# мог понимать эти логи. Формат KBE логов:
# INFO component_name [2023-01-01 00:00:01,000] - Whatever
_LOG_FORMAT = "%(levelname)s supervisor [%(asctime)s] - [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"  # noqa: E501
# Это дефолтный фиксированный порт для TCP сервера у KBEngine
_UDP_PORT = 20086


async def main() -> None:
    """Точка входа."""
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL), _LOG_FORMAT)

    app = Supervisor(
        udp_addr=Addr(settings.KBE_MACHINE_HOST, _UDP_PORT),
        tcp_addr=Addr(settings.KBE_MACHINE_HOST, settings.KBE_MACHINE_TCP_PORT),
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
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
