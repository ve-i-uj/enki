"""Уведомление Супервизора, что началась остановка компонента."""

import asyncio
import logging
import sys

from environs import Env, EnvError

from enki import msgspec, settings
from enki.kbetype.decoders.custom_decoders import KBEComponentId
from enki.misc import log
from enki.msg.message import Message
from enki.msg.msg_serializer import MessageSerializer
from enki.net.addr import Addr, Port
from enki.net.client import UDPClient

logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа."""
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    # Это самый наглядный способ получить при эксплуатации, какой переменной
    # не хватает
    env = Env()
    got_error = False

    kbe_machine_host = ""
    try:
        kbe_machine_host = env.str("KBE_MACHINE_HOST")
    except EnvError as err:
        got_error = True
        logger.error(err)

    kbe_machine_udp_port = 0
    try:
        kbe_machine_udp_port = env.int("KBE_MACHINE_UDP_PORT")
    except EnvError as err:
        got_error = True
        logger.error(err)

    kbe_component_id = 0
    try:
        kbe_component_id = env.int("KBE_COMPONENT_ID")
    except EnvError as err:
        got_error = True
        logger.error(err)

    kbe_component_name = ""
    try:
        kbe_component_name = env.str("KBE_COMPONENT_NAME")
    except EnvError as err:
        got_error = True
        logger.error(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    machine_addr = Addr(kbe_machine_host, Port(kbe_machine_udp_port))

    serializer = MessageSerializer(msgspec.SupervisorMsgSpecByID)

    msg = Message.create(
        msgspec.supervisor.onStopComponent,
        (KBEComponentId(kbe_component_id),),
    )
    data = serializer.serialize(msg)

    # Просто уведомление без ожидания ответа
    client = UDPClient(machine_addr)
    await client.send_data(data)

    logger.info(
        (
            "The '%s' (cid = %s) component is stopping. The notification has "
            "been sent to Supervisor"
        ),
        kbe_component_name,
        kbe_component_id,
    )
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
