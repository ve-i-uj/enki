import asyncio
import logging

from enki import settings
from enki.enkitype import AppAddr
from enki.net import msgspec
from enki.net.kbeclient import Client
from enki.net.command.machine import OnQueryAllInterfaceInfosCommand, OnQueryAllInterfaceInfosClient
from enki.misc import log

logger = logging.getLogger(__name__)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    client = OnQueryAllInterfaceInfosClient(
        settings.MACHINE_ADDR, msgspec.app.machine.SPEC_BY_ID
    )
    res = await client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{settings.MACHINE_ADDR}" server address '
                        f'(err="{res.text}")')
        return

    cmd = OnQueryAllInterfaceInfosCommand(
        client=client,
        uid=0,
        username='123',
        finderRecvPort=0
    )
    client.set_msg_receiver(cmd)
    resp = await cmd.execute()
    if not resp.success:
        logger.error(f'No response (err="{resp.text}")')
        return

    logger.info(f'Done (result = {resp.result})')


if __name__ == '__main__':
    asyncio.run(main())
