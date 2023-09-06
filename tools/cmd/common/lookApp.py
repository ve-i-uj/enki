"""Запросить живой ли компонент.

Для работы этой команды сперва нужно узнать внутренний адрес компонента,
т.к. соединения из вне скидываются (lookApp работает только у INTERNAL
подключений).
"""

import asyncio
import logging
import sys
from types import ModuleType
from typing import Optional

import environs

from enki import settings
from enki.command.common import RequestCommandResult
from enki.core.enkitype import AppAddr
from enki.core.kbeenum import ComponentType
from enki.core import msgspec
from enki.core.enkitype import AppAddr, Result
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.command import RequestCommand
from enki.handler.serverhandler.common import OnLookAppParsedData
from enki.misc import devonly, log
from enki.net import server

from tools.cmd.common import utils
from tools.cmd.common .utils import CachedComponentInfo, ComponentInfo, \
    NO_COMPONENT_ID, MachineAddr

logger = logging.getLogger(__name__)

_env = environs.Env()

KBE_MACHINE_HOST: str = _env.str('KBE_MACHINE_HOST')
KBE_MACHINE_UDP_PORT: int = _env.int('KBE_MACHINE_UDP_PORT', 20086)
KBE_MACHINE_TCP_PORT: int = _env.int('KBE_MACHINE_UDP_PORT', 20099)

KBE_COMPONENT_NAME: str = _env.str('KBE_COMPONENT_NAME')
KBE_COMPONENT_ID: int = _env.int('KBE_COMPONENT_ID', NO_COMPONENT_ID)
CACHE_ADDR: bool = _env.bool('CACHE_ADDR', False)


async def look_app(comp_type: ComponentType, host_ip: str,
                   machine_addr: MachineAddr) -> Result:
    logger.debug('%s', devonly.func_args_values())
    if comp_type.is_multiple_type():
        assert KBE_COMPONENT_ID != 0, 'Multiple components must have the "KBE_COMPONENT_ID" (it`s 0 now)'

    comp_info: Optional[ComponentInfo] = None

    if CACHE_ADDR:
        logger.info(f'Checking the cached address of the {comp_type.name} component ...')
        comp_info = CachedComponentInfo.get_comp_info(comp_type, KBE_COMPONENT_ID)

    if comp_info is None:
        logger.info(f'No cached address of the {comp_type.name} component. Request the address')
        comp_info_res = await utils.request_comp_info(
            comp_type, KBE_COMPONENT_ID, machine_addr, host_ip
        )
        if not comp_info_res.success:
            logger.error(comp_info_res.text)
            return Result(False, None, comp_info_res.text)

        comp_info = comp_info_res.result
        assert isinstance(comp_info, ComponentInfo)
        logger.info(f'The response of the component data has been received. '
                    f'The internal address of the component "{comp_type.name}" '
                    f'is "{comp_info.internal_address}"')
        if CACHE_ADDR:
            logger.info(f'Save the component info ...')
            CachedComponentInfo.save_cache_info(comp_info)

    # Ответ на lookApp у Baseapp и Cellapp отличаются по формату. Но первые
    # три поля одинаковые, а так как цель просто проверить живой компонент или
    # нет, то следующие поля после третьего у этих компонентов будут просто
    # отброщены при десериализации (это возможно за счёт того, что размер
    # onLookApp фиксированный).
    msg_spec_module: ModuleType = getattr(msgspec.app, comp_type.name.lower())
    cmd_lookApp = RequestCommand(
        comp_info.internal_address,
        Message(msg_spec_module.lookApp, tuple()),
        msgspec.custom.onLookApp.change_component_owner(comp_type),
        stop_on_first_data_chunk=True
    )
    logger.info(f'Checking is the "{comp_type.name}" component alive ...')
    res: RequestCommandResult = await cmd_lookApp.execute()
    if not res.success and CACHE_ADDR:
        logger.info(f'The component "{comp_type.name}" is not available on '
                    f'the address "{comp_info.internal_address}". Maybe '
                    f'cached data is not up to date. Try again without cache ...')
        # Возможно из кэша достали устаревшие данные. Попробуем ещё раз, но без кэша.
        comp_info_res = await utils.request_comp_info(
            comp_type, KBE_COMPONENT_ID, machine_addr, host_ip
        )
        if not comp_info_res.success:
            logger.error(res.text)
            return Result(False, None, res.text)

        comp_info = comp_info_res.result
        assert isinstance(comp_info, ComponentInfo)
        logger.info(f'The response of the component data has been received. '
                    f'The internal address of the component "{comp_type.name}" '
                    f'is "{comp_info.internal_address}"')

        CachedComponentInfo.delete_comp_info(comp_type, KBE_COMPONENT_ID)
        logger.info(f'Save the component info ...')
        CachedComponentInfo.save_cache_info(comp_info)

        # С новым адресом компонента попробуем проверить живой ли он (отправим lookApp)

        cmd_lookApp = RequestCommand(
            comp_info.internal_address,
            Message(msg_spec_module.lookApp, tuple()),
            msgspec.custom.onLookApp.change_component_owner(comp_type),
            stop_on_first_data_chunk=True
        )
        logger.info(f'Checking is the "{comp_type.name}" component alive ...')
        res = await cmd_lookApp.execute()

        # А дальше продолжается логика, как-будто не было перезапроса из-за
        # устаревшего кэша

    if not res.success:
        logger.error(f'The component "{comp_type.name}" is unavailable (err={res.text})')
        return Result(False, None, res.text)

    logger.info(f'The response from "{comp_type.name}" has been receive. '
                f'{comp_type.name} is alive')
    msgs = res.result
    msg = msgs[0]
    pd = OnLookAppParsedData(*msg.get_values())
    logger.info(f'"{comp_type.name}" lookApp data: {pd.asdict()}')

    return Result(True, pd)


async def main():
    log.setup_root_logger(logging.getLevelName(settings.LOG_LEVEL))
    comp_type: Optional[ComponentType] = getattr(ComponentType, KBE_COMPONENT_NAME.upper(), None)
    if comp_type is None:
        logger.error(f'Unknown component name "{KBE_COMPONENT_NAME}"')
        sys.exit(1)

    comp_name: str = KBE_COMPONENT_NAME
    if comp_type.is_multiple_type():
        comp_name = f'{KBE_COMPONENT_NAME}-{KBE_COMPONENT_ID}'
    logger.debug(f'The container name is "{comp_name}"')
    res = await look_app(
        comp_type,
        server.get_real_host_ip(comp_name),
        MachineAddr(
            KBE_MACHINE_HOST,
            KBE_MACHINE_TCP_PORT,
            KBE_MACHINE_UDP_PORT
        )
    )
    if not res.success:
        logger.error(res.text)
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    asyncio.run(main())
