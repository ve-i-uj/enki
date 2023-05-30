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
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.command import RequestCommand
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.handler.serverhandler.common import OnLookAppParsedData
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

MACHINE_ADDR = AppAddr(
    _env.str('KBE_MACHINE_HOST'),
    _env.int('KBE_MACHINE_TCP_PORT')
)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    cmd_lookApp = RequestCommand(
        MACHINE_ADDR,
        Message(msgspec.app.machine.lookApp, tuple()),
        msgspec.custom.onLookApp.change_component_owner(ComponentType.MACHINE),
        stop_on_first_data_chunk=True
    )
    res = await cmd_lookApp.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    msgs = res.result
    msg = msgs[0]
    pd = OnLookAppParsedData(*msg.get_values())

    logger.info(pd.asdict())
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
