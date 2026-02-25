"""Запросить живой ли компонент.

Для работы этой команды сперва нужно узнать внутренний адрес компонента,
т.к. соединения из вне скидываются (lookApp работает только у INTERNAL
подключений).
"""

import asyncio
import logging
import sys
from typing import TYPE_CHECKING

from environs import Env, EnvError

from enki import msgspec, settings
from enki.kbeenum import ComponentType
from enki.misc import devonly, log
from enki.misc.result import Result
from enki.msg.message import Message
from enki.msg.msg_client import RawRespTcpMsgClient
from enki.msg_parser.supervisor_msg_parser import (
    OnLookAppMsgParser,
)
from enki.net.addr import Port
from enki.net.server import get_real_host_ip
from enki.settings import SECOND
from tools.cmd.common import utils
from tools.cmd.common.utils import (
    CachedComponentInfo,
    ComponentInfo,
    MachineAddr,
)

if TYPE_CHECKING:
    from enki.msg.msg_descr import MsgDescr

logger = logging.getLogger(__name__)


async def look_app(
    comp_type: ComponentType,
    machine_addr: MachineAddr,
    cache_addr: bool,  # noqa: FBT001
    kbe_component_id: int,
) -> Result:
    """Получить данные запущенного компонента.

    Args:
        comp_type (ComponentType): тип компонента
        machine_addr (MachineAddr): адрес компонента Machine
        cache_addr (bool): нужно ли кэшировать адрес компонента
        kbe_component_id (int): идентификатор компонента

    Returns:
        Result: результат запроса

    """
    logger.debug("%s", devonly.func_args_values())

    comp_info: ComponentInfo | None = None

    if cache_addr:
        logger.info(
            "Checking the cached address of the %s component ...",
            comp_type.name,
        )
        comp_info = CachedComponentInfo.get_comp_info(
            comp_type, kbe_component_id
        )

    if comp_info is None:
        logger.info(
            "No cached address of the %s component. Request the address",
            comp_type.name,
        )
        comp_info_res = await utils.request_comp_info(
            comp_type, kbe_component_id, machine_addr
        )
        if not comp_info_res.success:
            logger.error(comp_info_res.text)
            return Result(success=False, result=None, text=comp_info_res.text)

        comp_info = comp_info_res.result
        assert comp_info is not None

    logger.info(
        "The response of the component data has been received. "
        'The internal address of the component "%s" is "%s"',
        comp_type.name,
        comp_info.internal_address,
    )
    if cache_addr:
        logger.info("Save the component info ...")
        CachedComponentInfo.save_cache_info(comp_info)

    # Ответ на lookApp у Baseapp и Cellapp отличаются по формату. Но первые
    # три поля одинаковые, а так как цель просто проверить живой компонент или
    # нет, то следующие поля после третьего у этих компонентов будут просто
    # отброщены при десериализации (это возможно за счёт того, что размер
    # onLookApp фиксированный).
    logger.info('Checking is the "%s" component alive ...', comp_type.name)

    client = RawRespTcpMsgClient(
        comp_info.internal_address, msgspec.machine.onLookApp
    )
    res = await client.start()
    if not res.success and cache_addr:
        logger.info(
            'The component "%s" is not available on the address "%s". Maybe '
            "cached data is not up to date. Try again without cache ...",
            comp_type.name,
            comp_info.internal_address,
        )
        # Возможно из кэша достали устаревшие данные. Попробуем ещё раз, но без
        # кэша.
        comp_info_res = await utils.request_comp_info(
            comp_type, kbe_component_id, machine_addr
        )
        if not comp_info_res.success:
            logger.error(res.text)
            return Result(success=False, result=None, text=res.text)

        comp_info = comp_info_res.result
        assert comp_info is not None

        logger.info(
            "The response of the component data has been received. "
            'The internal address of the component "%s" '
            'is "%s"',
            comp_type.name,
            comp_info.internal_address,
        )

        CachedComponentInfo.delete_comp_info(comp_type, kbe_component_id)
        logger.info("Save the component info ...")
        CachedComponentInfo.save_cache_info(comp_info)

        # С новым адресом компонента попробуем проверить живой ли он
        # (подключиться к нему)

        client = RawRespTcpMsgClient(
            comp_info.internal_address, msgspec.machine.onLookApp
        )
        res = await client.start()
        if not res.success:
            logger.error(res.text)
            return Result(success=False, result=None, text=res.text)

        # А дальше продолжается логика, как-будто не было перезапроса из-за
        # устаревшего кэша

    # Сообщение ::lookApp у разных компонентов имеет разный id. Поэтому нужно
    # доставать описание сообщения динамически в зависимости от компонента
    lookApp_descr: MsgDescr = getattr(
        msgspec, comp_type.name.lower()
    ).lookApp  # pylint: disable=invalid-name
    msg = Message.create(lookApp_descr, ())
    success = await client.send_msg(msg)
    if not success:
        text = f"The message '{msg.name}' is not sent"
        logger.error(text)
        return Result(success=False, result=None, text=text)

    resp_msg = await client.wait_only_first_resp_msg(5 * SECOND)
    if resp_msg is None:
        text = f"There is no response message on '{msg.name}'"
        logger.error(text)
        return Result(success=False, result=None, text=text)

    logger.info(
        'The response from "%s" has been receive. %s is alive',
        comp_type.name,
        comp_type.name,
    )
    pd = OnLookAppMsgParser().parse(resp_msg).result

    logger.info('"%s" lookApp data: %s', comp_type.name, pd.asdict())
    return Result(success=True, result=pd)


async def main() -> None:
    """Точка входа для запуска команды ::lookApp ."""
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))

    # Это самый наглядный способ получить при эксплуатации, какой переменной
    # не хватает
    env = Env()
    got_error = False

    kbe_machine_host = ""
    try:
        kbe_machine_host = env.str("KBE_MACHINE_HOST")
    except EnvError as err:
        kbe_machine_host = ""
        got_error = True
        logger.warning(err)

    kbe_machine_udp_port = 0
    try:
        kbe_machine_udp_port = env.int("KBE_MACHINE_UDP_PORT")
    except EnvError as err:
        got_error = True
        logger.warning(err)

    kbe_machine_tcp_port = 0
    try:
        kbe_machine_tcp_port = env.int("KBE_MACHINE_TCP_PORT")
    except EnvError as err:
        kbe_machine_tcp_port = -1
        got_error = True
        logger.warning(err)

    kbe_component_id = 0
    try:
        kbe_component_id = env.int("KBE_COMPONENT_ID")
    except EnvError as err:
        kbe_component_id = -1
        got_error = True
        logger.warning(err)

    kbe_component_name = ""
    try:
        kbe_component_name = env.str("KBE_COMPONENT_NAME")
    except EnvError as err:
        kbe_component_name = ""
        got_error = True
        logger.warning(err)

    cache_addr = False
    try:
        cache_addr = env.bool("CACHE_ADDR")
    except EnvError as err:
        got_error = True
        cache_addr = False
        logger.warning(err)

    if got_error:
        logger.error("Failed to load environment variables")
        sys.exit(1)

    comp_type: ComponentType | None = getattr(
        ComponentType, kbe_component_name.upper(), None
    )
    if comp_type is None:
        logger.error('Unknown component name "%s"', kbe_component_name)
        sys.exit(1)

    comp_name: str = kbe_component_name
    if comp_type.is_multiple_type():
        comp_name = f"{kbe_component_name}-{kbe_component_id}"
    logger.debug('The container name is "%s"', comp_name)

    res = await look_app(
        comp_type,
        MachineAddr(
            get_real_host_ip(kbe_machine_host),
            Port(kbe_machine_tcp_port),
            Port(kbe_machine_udp_port),
        ),
        cache_addr,
        kbe_component_id,
    )
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
