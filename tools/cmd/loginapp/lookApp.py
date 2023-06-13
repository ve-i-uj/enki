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
KBE_COMPONENT_ID: int = _env.int('KBE_COMPONENT_ID')
CACHE_ADDR = _env.bool('CACHE_ADDR', False)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    service_name = f'{KBE_COMPONENT_NAME}'
    res = await cmdcommon.look_app(
        ComponentType.LOGINAPP, server.get_real_host_ip(service_name),
        MACHINE_ADDR, CACHE_ADDR, 0
    )
    if not res.success:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
