import asyncio
import logging
import sys

import environs

from enki import settings

from enki.core.enkitype import AppAddr
from enki.core import msgspec
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

# The Machine address
_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
_MACHINE_PORT: int = _env.int('KBE_MACHINE_TCP_PORT')
MACHINE_ADDR = AppAddr(_MACHINE_HOST, _MACHINE_PORT)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    cmd = OnQueryAllInterfaceInfosCommand(MACHINE_ADDR)
    resp = await cmd.execute()
    if not resp.success:
        logger.error(f'No response (err="{resp.text}")')
        sys.exit(1)

    import pprint
    from dataclasses import asdict
    dcts = asdict(resp.result)
    dct_lst: list[dict] = dcts['infos']
    for i, info in enumerate(resp.result.infos):
            dct_lst[i].update(info.asdict())

    pprint.pprint(dcts)
    # logger.info(f'Done (result = {resp.result})')
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
