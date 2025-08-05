"""Запросить из контейнера адрес компонента.

Команда предназначена для выполнения из контейнера Docker, т.к. ответ
отправляется на UDP хост:порт, а это подразумевает, что между хостом и
контейнером должны быть открыты порты.
"""

import asyncio
import logging
import pprint
import sys

from environs import Env, EnvError

from enki import settings
from enki.command.machine import OnFindInterfaceAddrCommand
from enki.kbeenum import ComponentType
from enki.misc import log
from enki.net.addr import Addr, Port
from enki.net.server import get_real_host_ip

logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа."""
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    env = Env()
    got_error = False
    try:
        kbe_machine_host = env.str("KBE_MACHINE_HOST")
    except EnvError as err:
        got_error = True
        logger.warning(err)
    try:
        kbe_machine_udp_port = env.int("KBE_MACHINE_UDP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)
    try:
        find_component = env.str("FIND_COMPONENT")
    except EnvError as err:
        got_error = True
        logger.warning(err)
    try:
        kbe_component_id = env.int("KBE_COMPONENT_ID")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    machine_addr = Addr(
        get_real_host_ip(kbe_machine_host), Port(kbe_machine_udp_port)
    )
    comp_type: ComponentType | None = getattr(
        ComponentType, find_component.upper(), None
    )
    if comp_type is None:
        logger.error('There is component type "%s"', find_component)
        sys.exit(1)

    cmd = OnFindInterfaceAddrCommand(
        machine_addr, 1000, "root", comp_type, kbe_component_id
    )
    res = await cmd.execute()
    if not res.success:
        logger.error('No response (err="%s")', res.text)
        sys.exit(1)

    assert res.result is not None

    if res.result.component_type == ComponentType.UNKNOWN_COMPONENT:
        text = f'The component "{comp_type.name}" is not registered'
        logger.error(text)
        sys.exit(0)

    logger.info("Done (result = %s)", pprint.pformat(res.result.asdict()))
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
