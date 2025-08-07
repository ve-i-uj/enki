"""Оправить компоненту сообщение об остановке.

Для работы этой команды сперва нужно узнать внутренний адрес компонента,
т.к. соединения из вне скидываются (reqCloseServer работает только у INTERNAL
подключений).
"""

import asyncio
import logging
import sys

from environs import Env, EnvError

from enki import msgspec, settings
from enki.kbeenum import ComponentType
from enki.misc import devonly, log
from enki.misc.result import Result
from enki.msg.message import Message
from enki.msg.msg_client import RawRespTcpMsgClient
from enki.net.addr import Port
from enki.net.server import get_real_host_ip
from enki.settings import SECOND
from tools.cmd.common import utils
from tools.cmd.common.utils import MachineAddr

logger = logging.getLogger(__name__)


async def req_close_server(
    machine_addr: MachineAddr, comp_type: ComponentType, comp_id: int
) -> Result:
    """Отправить компоненту сообщение ::reqCloseServer.

    Args:
        machine_addr (MachineAddr): адрес компонента Machine
        comp_type (ComponentType): тип компонента, которому будет отправлено
            сообщение
        comp_id (int): id компонента (cid)

    Returns:
        Result: объект результата выполнения

    """
    logger.debug("%s", devonly.func_args_values())

    comp_info_res = await utils.request_comp_info(
        comp_type, comp_id, machine_addr
    )
    if not comp_info_res.success:
        # На Machine компонент не регистрировался, значит и не запушен
        return Result(success=False, result=None, text=comp_info_res.text)

    # В этой точке есть инфа о компоненте

    comp_info = comp_info_res.result
    assert comp_info is not None

    module = getattr(msgspec, comp_type.name.lower())
    if not hasattr(module, "reqCloseServer"):
        err_text = f"The '{comp_type.name}' has no message 'reqCloseServer'"
        logger.error(err_text)
        return Result(success=False, result=None, text=err_text)
    reqCloseServer_descr = module.reqCloseServer  # noqa: N806
    reqCloseServer_msg = Message.create(reqCloseServer_descr, ())  # noqa: N806

    # Динамически получаем описание фейкового сообщения ::onReqCloseServer,
    # только с уже нужным компонентом владельцем
    resp_msg_descr = getattr(msgspec, comp_type.name.lower()).onReqCloseServer
    client = RawRespTcpMsgClient(
        comp_info.internal_address,
        resp_msg_descr,
    )

    res = await client.start()
    if not res.success:
        logger.error(
            "It cannot be connect to the component '%s' (cid = %s, reason = '%s')",  # noqa: E501
            comp_type.name,
            comp_id,
            res.text,
        )
        return Result(success=False, result=None, text=res.text)

    logger.info("Send request to stop to the '%s' component ...", comp_type.name)
    success = await client.send_msg(reqCloseServer_msg)
    if success:
        err_text = (
            f"The message '{reqCloseServer_msg.name}' has not been sent "
            f"(component = '{comp_type.name}', cid = {comp_id})"
        )
        logger.error("%s", err_text)
        return Result(success=False, result=None, text=err_text)

    resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
    if resp_msg is None:
        # Компоненты в любом случае отправляют true. Если ничего не пришло,
        # значит адресат или скинул сообщение, или не получил, или клиент по
        # таймауту
        err_text = (
            f'The component "{comp_type.name}" (cid = "{comp_id}") has '
            f"not responsed"
        )
        logger.error("%s", err_text)
        return Result(success=False, result=None, text=err_text)

    logger.info(
        "The message to stop have been received by the "
        '"%s" (cid = "%s") component',
        comp_type.name,
        comp_id,
    )
    return Result(success=True, result=None)


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
        kbe_machine_tcp_port = env.int("KBE_MACHINE_TCP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)
    try:
        kbe_component_name = env.str("KBE_COMPONENT_NAME")
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

    comp_type = getattr(ComponentType, kbe_component_name.upper(), None)
    if comp_type is None:
        logger.error('Unknown component name "%s"', kbe_component_name)
        sys.exit(1)

    res = await req_close_server(
        MachineAddr(
            get_real_host_ip(kbe_machine_host),
            Port(kbe_machine_tcp_port),
            Port(kbe_machine_udp_port),
        ),
        comp_type,
        kbe_component_id,
    )
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
