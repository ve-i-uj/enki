import asyncio
import collections
import logging
import sys
from enki.core import msgspec
from enki.core.kbeenum import ComponentType
from enki.core.message import Message

from enki.misc import log, devonly
from enki.core.enkitype import AppAddr, Result
from enki.core import msgspec
from enki.net.server import UDPServer
from enki.net.inet import IAppComponent, IChannel, IServerMsgReceiver
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceHandler, OnBroadcastInterfaceHandlerResult, OnBroadcastInterfaceParsedData

from enki.app.supervisor.supervisorapp import Supervisor
from enki.app.supervisor import settings

logger = logging.getLogger(__name__)

# Формат нужно задать такой же, как и остальных компонентов, чтобы LogStash
# мог понимать эти логи. Формат KBE логов:
# INFO component_name [2023-01-01 00:00:01,000] - Whatever
_LOG_FORMAT = '%(levelname)s supervisor [%(asctime)s] - [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'


async def main():
    # log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    log.setup_root_logger('DEBUG', _LOG_FORMAT)
    logger.info('Done')

    app = Supervisor(AppAddr(settings.KBE_MACHINE_HOST, settings.KBE_MACHINE_PORT))
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
        app.stop()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
