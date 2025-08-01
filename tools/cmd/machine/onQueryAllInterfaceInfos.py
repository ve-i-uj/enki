"""Скрипт для запроса Machine::onQueryAllInterfaceInfos."""

import asyncio
import logging
import pprint
import sys

from environs import Env, EnvError

from enki import settings
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.misc import log
from enki.net.addr import Addr, Port

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

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    machine_addr = Addr(kbe_machine_host, Port(kbe_machine_udp_port))
    cmd = OnQueryAllInterfaceInfosCommand(machine_addr)

    res = await cmd.execute()
    if not res.success:
        logger.error(
            "[%s] The command is not executed (reason = %s)", cmd, res.text
        )
        sys.exit(1)

    assert res.result is not None

    dct = {}
    for i, info in enumerate(res.result.infos):
        dct[i] = info.asdict()

    logger.info("Done (result = %s)", pprint.pformat(dct))
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
