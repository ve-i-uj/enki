"""Запросить живой ли компонент.

Для работы этой команды сперва нужно узнать внутренний адрес компонента,
т.к. соединения из вне скидываются (lookApp работает только у INTERNAL
подключений).
"""

import asyncio
import logging
import sys

import environs

from enki import settings
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.misc import log
from enki.net import server

from tools import cmdcommon

logger = logging.getLogger(__name__)

_env = environs.Env()

KBE_MACHINE_UDP_PORT=20086
MACHINE_ADDR = AppAddr(
    _env.str('KBE_MACHINE_HOST'),
    KBE_MACHINE_UDP_PORT
)
KBE_COMPONENT_NAME: str = _env.str('KBE_COMPONENT_NAME')
HEALTHCHECK_CACHED_ADDR = _env.bool('HEALTHCHECK_CACHED_ADDR', False)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    res = await cmdcommon.look_app(
        ComponentType.LOGGER, server.get_real_host_ip(KBE_COMPONENT_NAME),
        MACHINE_ADDR, HEALTHCHECK_CACHED_ADDR, 0
    )
    if not res.success:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
