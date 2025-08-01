"""Уведомление Супервизора, что началась остановка компонента."""

import asyncio
import logging
import pprint
import sys

import environs

from enki import settings
from enki.misc import log
from enki.core.message import Message
from enki.net.addr import Addr
from enki.kbeenum import ComponentType
from enki.core import kbepickle, msgspec
from enki.handlers.server_handlers.machinehandler import QueryComponentIDParsedData
from enki.net import server

from enki.command.machine import QueryComponentIDCommand
from enki.net.client import TCPClient, UDPClient

logger = logging.getLogger(__name__)

_env = environs.Env()

# ЭТО UDP адрес машины
_MACHINE_HOST: str = _env.str("KBE_MACHINE_HOST")
_MACHINE_PORT: int = _env.int("KBE_MACHINE_UDP_PORT", 20086)
MACHINE_ADDR = Addr(_MACHINE_HOST, _MACHINE_PORT)

KBE_COMPONENT_ID: int = _env.int("KBE_COMPONENT_ID")


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    serializer = kbepickle.get_serializer_for(ComponentType.MACHINE)

    msg = Message(msgspec.app.supervisor.onStopComponent, tuple([KBE_COMPONENT_ID]))
    data = serializer.serialize(msg)

    client = UDPClient(MACHINE_ADDR)
    success = await client.send_data(data)
    if not success:
        logger.error(f'The message "{msg.name}" hasn`t been sent')
        sys.exit(1)

    logger.info(f"The stopping notification has been sent to Supervisor")
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
