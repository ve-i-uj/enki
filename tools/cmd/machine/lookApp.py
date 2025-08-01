#!/usr/bin/env python

"""Скрипт, проверяющий жив ли компонент Machine / Supervisor.

На компонент отправляется Machine::lookApp.

Необходимо узнать внутренний адрес
компонента, поскольку внешние соединения отбрасываются (lookApp работает только
для ВНУТРЕННИХ соединений). Однако, этот скрипт используется для проверки
работоспособности компонента
Supervisor. Supervisor имеет API компонента «Machine», но у него нет
ограничения на ВНУТРЕННИЙ адрес, поэтому скрипт получит ответ даже от внешнего
tcp-адреса компонента Supervisor.
"""

import asyncio
import logging
import sys

import environs

from enki import msgspec
from enki.misc.log import setup_root_logger
from enki.msg.message import Message
from enki.msg.msg_client import RawRespTcpMsgClient
from enki.msg_parser.supervisor_msg_parser import OnLookAppMsgParser
from enki.net.addr import Addr
from enki.settings import SECOND

logger = logging.getLogger(__name__)

_env = environs.Env()

MACHINE_ADDR = Addr(
    _env.str("KBE_MACHINE_HOST"), _env.int("KBE_MACHINE_TCP_PORT")
)
LOG_LEVEL: int = _env.log_level("LOG_LEVEL", logging.INFO)


async def main() -> None:
    """Точка входа для запуска скрипта."""

    machine_host = _env.str("KBE_MACHINE_HOST")
    _env.int("KBE_MACHINE_TCP_PORT")
    _env.log_level("LOG_LEVEL", logging.INFO)

    setup_root_logger(logging.getLevelName(LOG_LEVEL))

    # Создаем клиент с потоковым ответом
    client = RawRespTcpMsgClient(MACHINE_ADDR, msgspec.supervisor.onLookApp)

    # Запускаем клиент
    res = await client.start()
    if not res.success:
        logger.error("Failed to start client: %s", res.text)
        sys.exit(1)

    # Создаем и отправляем сообщение
    msg = Message(
        msgspec.machine.lookApp.id,
        msgspec.machine.lookApp.name,
        msgspec.machine.lookApp.component_type,
        (),
    )

    logger.info("Sending the message '%s'", msg.name)
    success = await client.send_msg(msg)
    if not success:
        logger.error("Failed to send message")
        sys.exit(1)

    # Ожидаем ответ
    resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
    if resp_msg is None:
        logger.error("No response received")
        sys.exit(1)

    # Парсим полученное сообщение
    parser_res = OnLookAppMsgParser().parse(resp_msg)
    if not parser_res.success:
        logger.error(
            "The message '%s' cannot be parsed (%s)",
            msgspec.supervisor.onLookApp.name,
            parser_res.text,
        )
        sys.exit(1)

    pd = parser_res.result
    logger.info("'%s' response: %s", msg.name, pd.asdict())

    # Останавливаем клиент
    client.stop()
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
