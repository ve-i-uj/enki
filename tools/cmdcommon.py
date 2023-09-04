"""Запросить живой ли компонент.

Для работы этой команды сперва нужно узнать внутренний адрес компонента,
т.к. соединения из вне скидываются (lookApp работает только у INTERNAL
подключений).
"""

import logging
from pathlib import Path
from types import ModuleType
from typing import Optional

from enki.core import msgspec
from enki.core.enkitype import AppAddr, Result
from enki.core.kbeenum import ComponentType
from enki.core.message import Message
from enki.command.machine import OnFindInterfaceAddrTCPCommand, OnFindInterfaceAddrUDPCommand
from enki.command import RequestCommand
from enki.handler.serverhandler.common import OnLookAppParsedData
from enki.handler.serverhandler.machinehandler import OnBroadcastInterfaceParsedData, OnFindInterfaceAddrParsedData
from enki.misc import devonly
from enki.net import server

logger = logging.getLogger(__name__)

_CACHED_DATA_DIR = Path('/tmp/enki/cache')
_CACHED_DATA_DIR.mkdir(parents=True, exist_ok=True)


async def look_app(comp_type: ComponentType, host_ip: str, machine_addr: AppAddr,
                   cache_data: bool, component_id: int) -> Result:
    logger.debug('%s', devonly.func_args_values())
    if comp_type.is_multiple_type():
        assert component_id != 0
    # Чтобы не забивать запросами Машину воспользуемся закэшированными
    # данными о запрашиваемом компоненте.
    comp_info: Optional[OnBroadcastInterfaceParsedData] = None
    cached_data_path = _CACHED_DATA_DIR / f'{comp_type.name}.cached'
    if cache_data:
        cached_data_path.touch(exist_ok=True)
        logger.info(f'Read the {comp_type.name} cached info ...')
        with cached_data_path.open() as fh:
            text = fh.read()
        try:
            comp_info = OnBroadcastInterfaceParsedData.from_json(text)
            logger.info(f'The cached {comp_type.name} info exists')
        except ValueError:
            logger.info(f'There is no cached info in the "{cached_data_path}" file')

    if comp_info is None:
        logger.info(f'Request the internal {comp_type.name} address ...')
        req_pd = OnFindInterfaceAddrParsedData(
            uid=1000,
            username='root',
            componentType=ComponentType.UNKNOWN_COMPONENT,
            componentID=0,
            findComponentType=comp_type.value,
            addr=0,
            finderRecvPort=0
        )
        if comp_type.is_multiple_type():
            cmd = OnFindInterfaceAddrTCPCommand(machine_addr, req_pd)
            res = await cmd.execute()
            if not res.success:
                text = f'No response from Machine (err="{res.text}")'
                logger.error(text)
                return Result(False, None, text)

            comp_info: Optional[OnBroadcastInterfaceParsedData] = None
            for info in res.result.infos:
                # Это данные компонента, который мы запрашивали
                if info.componentID == component_id:
                    comp_info = info
                    break
            # Эта процедура используется для хэлсчека запущенного компонента.
            # Точно известен его id под которым он должен был зарегистрироваться
            # при старте. Если он не найден - это или компонент не стартанул,
            # или ошибка в логике.
            if comp_info is None:
                text = (f'There is no reqistered component "{comp_type}" '
                             f'(cid={component_id})')
                logger.error(text)
                return Result(False, None, text)
        else:
            req_pd.callback_address = AppAddr(host_ip, server.get_free_port())
            cmd = OnFindInterfaceAddrUDPCommand(machine_addr, req_pd)
            res = await cmd.execute()
            if not res.success:
                text = f'No response from Machine (err="{res.text}")'
                logger.error(text)
                return Result(False, None, text)
            comp_info = res.result
            assert comp_info is not None

        if comp_info.component_type == ComponentType.UNKNOWN_COMPONENT:
            text = f'The component "{comp_type.name}" is not registered'
            logger.error(text)
            return Result(False, None, text)

        logger.info(f'The response from Machine has been received. The internal '
                    f'{comp_type.name} address is "{comp_info.internal_address}"')

        if cache_data:
            logger.info(f'Save received data to the file "{cached_data_path}"')
            with cached_data_path.open('w') as fh:
                fh.write(comp_info.to_json(comp_info))

    # Ответ на lookApp у Baseapp и Cellapp отличаются по формату. Но первые
    # три поля одинаковые, а так как цель просто проверить живой компонент или
    # нет, то следующие поля после третьего у этих компонентов будут просто
    # отброщены при десериализации. (это возможно за счёт того, что размер
    # onLookApp фиксированный).
    msg_spec_module: ModuleType = getattr(msgspec.app, comp_type.name.lower())
    cmd_lookApp = RequestCommand(
        comp_info.internal_address,
        Message(msg_spec_module.lookApp, tuple()),
        msgspec.custom.onLookApp.change_component_owner(comp_type),
        stop_on_first_data_chunk=True
    )
    logger.info(f'Checking is {comp_type.name} alive ...')
    res = await cmd_lookApp.execute()
    if not res.success and cache_data:
        logger.info(f'The component "{comp_type.name}" is not available on '
                    f'the address "{comp_info.internal_address}". Maybe '
                    f'cached data is not up to date. Try again without cache ...')
        # Возможно из кэша достали устаревшие данные. Попробуем ещё раз, но без кэша.
        res = await look_app(
            comp_type, host_ip, machine_addr, cache_data=False,
            component_id=component_id
        )
        # В любом случае надо удалить старый кэш, а затем записать новые данные,
        # если они есть.
        logger.info(f'Delete not actual cache file "{cached_data_path}"')
        cached_data_path.unlink()
        if res.success:
            logger.info(f'Save received data to the file "{cached_data_path}"')
            with cached_data_path.open('w') as fh:
                fh.write(comp_info.to_json(comp_info))
            pd: OnLookAppParsedData = res.result
            logger.info(f'"{comp_type.name}" lookApp data: {pd.asdict()}')
            return Result(True, pd)

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
