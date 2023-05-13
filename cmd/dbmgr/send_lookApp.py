import asyncio
import logging
import socket
import sys
import tempfile
from pathlib import Path

import environs

from enki import settings
from enki.core import kbeenum
from enki.core.enkitype import AppAddr
from enki.net.client import StreamClient
from enki.core import msgspec
from enki.command.dbmgr import DBMgrLookAppCommand
from enki.command.machine import OnQueryAllInterfaceInfosCommand
from enki.misc import log

logger = logging.getLogger(__name__)

_env = environs.Env()

MACHINE_ADDR = AppAddr(
    _env.str('KBE_MACHINE_HOST'),
    _env.int('KBE_MACHINE_PORT')
)
DBMGR_HOST = _env.str('KBE_DBMGR_HOST')
CACHED_PORT = _env.bool('KBE_DBMGR_CACHED_PORT', False)

CACHED_PORT_PATH = Path(tempfile.gettempdir()) / 'dbmgr_port.cached' # type: ignore


async def request_cluster_infos():
    machine_client = StreamClient(
        MACHINE_ADDR,
        msgspec.app.machine.SPEC_BY_ID
    )
    res = await machine_client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{MACHINE_ADDR}" server'
                     f' address (err="{res.text}")')
        sys.exit(1)

    cmd = OnQueryAllInterfaceInfosCommand(
        client=machine_client,
        uid=0,
        username='123',
        finderRecvPort=0
    )
    machine_client.set_msg_receiver(cmd)
    res = await cmd.execute()

    return res


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    dbmgr_port = 0
    if CACHED_PORT:
        CACHED_PORT_PATH.touch()
        with CACHED_PORT_PATH.open() as fh:
            text = fh.read()
        try:
            dbmgr_port = int(text.strip())
            logger.info(f'The DBMgr port is from the cache ({dbmgr_port})')
        except ValueError:
            logger.info(f'There is no cached dbmgr port in the "{CACHED_PORT_PATH}" file')

    if not dbmgr_port:
        logger.info('Request the dbmgr port from Machine')
        res = await request_cluster_infos()
        if not res.get_info(kbeenum.ComponentType.DBMGR_TYPE):
            logger.error(f'Cannot get the DBMgr port (cluster info = {res})')
            sys.exit(1)

        dbmgr_port = socket.ntohs(
            res.get_info(kbeenum.ComponentType.DBMGR_TYPE)[0].intport
        )
        logger.info(f'The dbmgr port from Machine is "{dbmgr_port}"')

        if CACHED_PORT:
            with CACHED_PORT_PATH.open('w') as fh:
                fh.write(str(dbmgr_port))
            logger.info(f'The dbmgr port is cached in the "{CACHED_PORT_PATH}" file')

    dbmgr_addr = AppAddr(DBMGR_HOST, dbmgr_port)
    dbmgr_client = StreamClient(dbmgr_addr, msgspec.app.dbmgr.SPEC_BY_ID)
    res = await dbmgr_client.start()
    if not res.success:
        logger.error(f'Cannot connect to the "{dbmgr_addr}" server'
                     f' address (err="{res.text}")')
        sys.exit(1)

    cmd = DBMgrLookAppCommand(dbmgr_client)
    dbmgr_client.set_msg_receiver(cmd)

    res = await cmd.execute()
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    logger.info(res.result)
    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
