"""Запросить из контейнера адрес компонента.

Команда предназначена для выполнения из контейнера Docker, т.к. ответ
отправляется на UDP хост:порт, а это подразумевает, что между хостом и
контейнером должны быть открыты порты.
"""

import asyncio
import logging
import sys
from typing import Optional

import environs

from enki import settings

from enki.misc import log
from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.core.kbeenum import ComponentType
from enki.command.machine import OnFindInterfaceAddrUDPCommand, OnQueryAllInterfaceInfosCommand
from enki.handler.serverhandler.machinehandler import OnFindInterfaceAddrHandler, OnFindInterfaceAddrParsedData
from enki.net import server

logger = logging.getLogger(__name__)

_env = environs.Env()

_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
_MACHINE_UDP_PORT = 20086
MACHINE_ADDR = AppAddr(_MACHINE_HOST, _MACHINE_UDP_PORT)

FIND_COMPONENT: str = _env.str('FIND_COMPONENT')
# Имя будет использовано, как адрес для ожидания ответа от Машины
KBE_COMPONENT_NAME: str = _env.str('KBE_COMPONENT_NAME')


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    comp_type: Optional[ComponentType] = getattr(ComponentType, FIND_COMPONENT.upper(), None)
    if comp_type is None:
        logger.error(f'There is component type "{FIND_COMPONENT}"')
        sys.exit(1)

    req_pd = OnFindInterfaceAddrParsedData(
        uid=1000,
        username='root',
        componentType=ComponentType.UNKNOWN_COMPONENT,
        componentID=0,
        findComponentType=comp_type.value,
        addr=0,
        finderRecvPort=0
    )
    req_pd.callback_address = AppAddr(
        server.get_real_host_ip(KBE_COMPONENT_NAME),
        server.get_free_port()
    )
    cmd = OnFindInterfaceAddrUDPCommand(MACHINE_ADDR, req_pd)
    res = await cmd.execute()
    if not res.success:
        logger.error(f'No response (err="{res.text}")')
        sys.exit(1)

    assert res.result is not None
    if res.result.component_type == ComponentType.UNKNOWN_COMPONENT:
        text = f'The component "{comp_type.name}" is not registered'
        logger.error(text)
        sys.exit(1)

    logger.info(res.result.asdict())
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
