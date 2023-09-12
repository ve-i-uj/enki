"""Запросить из консоли componentID у Машины.

KBE_MACHINE_HOST='0.0.0.0' KBE_MACHINE_UDP_PORT=20086
"""

import asyncio
import logging
import pprint
import sys

import environs

from enki import settings
from enki.misc import log
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.core import msgspec
from enki.handler.serverhandler.machinehandler import QueryComponentIDParsedData
from enki.net import server

from enki.command.machine import QueryComponentIDCommand

logger = logging.getLogger(__name__)

_env = environs.Env()

# ЭТО UDP адрес машины
_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
_MACHINE_PORT: int = _env.int('KBE_MACHINE_UDP_PORT', 20086)

MACHINE_ADDR = AppAddr(_MACHINE_HOST, _MACHINE_PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    pd = QueryComponentIDParsedData(
        componentType=ComponentType.UNKNOWN_COMPONENT,
        componentID=0,
        uid=0,
        finderRecvPort=0,
        macMD5=0,
        pid=0
    )
    pd.callback_port = server.get_free_port()
    cmd = QueryComponentIDCommand(MACHINE_ADDR, pd)
    res = await cmd.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    assert res.result is not None
    pprint.pprint(res.result.asdict())

    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
