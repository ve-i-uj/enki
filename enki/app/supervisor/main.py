import asyncio
import logging
import sys

from enki.misc import log
from enki.core.enkitype import AppAddr

from enki.app.supervisor.supervisorapp import Supervisor
from enki.app.supervisor import settings

logger = logging.getLogger(__name__)

# Формат нужно задать такой же, как и остальных компонентов, чтобы LogStash
# мог понимать эти логи. Формат KBE логов:
# INFO component_name [2023-01-01 00:00:01,000] - Whatever
LOG_FORMAT = '%(levelname)s supervisor [%(asctime)s] - [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
# Это дефолтный фиксированный порт для TCP сервера у KBEngine
UDP_PORT = 20086


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL), LOG_FORMAT)
    logger.info('Done')

    app = Supervisor(
        udp_addr=AppAddr(settings.KBE_MACHINE_HOST, UDP_PORT),
        tcp_addr=AppAddr(settings.KBE_MACHINE_HOST, settings.KBE_MACHINE_TCP_PORT),
    )
    try:
        res = await app.start()
        if not res.success:
            logger.error('UDP server cannot start. Error %s', res.text)
            sys.exit(1)

        loop = asyncio.get_running_loop()
        future = asyncio.Future()
        await future
        logger.info('Done')
    except Exception as err:
        logger.error(err, exc_info=True)
    finally:
        await app.stop()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
