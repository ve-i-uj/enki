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

from environs import Env, EnvError

from enki import msgspec
from enki import settings
from enki.misc.log import setup_root_logger
from enki.msg.message import Message
from enki.msg.msg_client import RawRespTcpMsgClient
from enki.msg_parser.supervisor_msg_parser import OnLookAppMsgParser
from enki.net.addr import Addr, Port
from enki.settings import SECOND

logger = logging.getLogger(__name__)


async def main() -> None:
    """Точка входа для запуска скрипта."""
    setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    # Это самый наглядный способ получить при эксплуатации, какой переменной
    # не хватает
    env = Env()
    got_error = False
    try:
        kbe_machine_host = env.str("KBE_MACHINE_HOST")
    except EnvError as err:
        got_error = True
        logger.error(err)  # noqa: TRY400
    try:
        kbe_machine_tcp_port = env.int("KBE_MACHINE_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.error(err)  # noqa: TRY400

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    # Создаем клиент с потоковым ответом
    client = RawRespTcpMsgClient(
        Addr(kbe_machine_host, Port(kbe_machine_tcp_port)),
        msgspec.supervisor.onLookApp,
    )

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
